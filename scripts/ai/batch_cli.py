"""
Batch processor using Claude CLI instead of API
"""

import time
import json
from pathlib import Path
from typing import Optional, List, Dict, Callable
from dataclasses import dataclass

from .cli_client import ClaudeCLIClient, Message
from .conversation import ConversationManager
from .prompts import PromptTemplates


@dataclass
class RuleExtractionResult:
    """Result from extracting a single rule"""
    rule_number: int
    success: bool
    content: str
    end_page: int
    error: Optional[str] = None


class BatchProcessorCLI:
    """
    Batch processor using Claude CLI (subscription-based)

    Features:
    - Uses terminal claude command
    - No API costs (subscription-based)
    - No rate limits
    - Sequential rule extraction
    - Progress tracking
    - Resume from checkpoint
    """

    def __init__(
        self,
        structured_pages_dir: Path,
        output_dir: Path,
    ):
        """
        Initialize batch processor

        Args:
            structured_pages_dir: Directory with Phase 2 output
            output_dir: Directory for extracted rules
        """
        self.structured_pages_dir = Path(structured_pages_dir)
        self.output_dir = Path(output_dir)
        self.client = ClaudeCLIClient()

        # State tracking
        self.current_page = 1
        self.checkpoint_file = self.output_dir / ".checkpoint.json"

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print("✓ Using Claude CLI (subscription-based, no API costs)")

    def load_checkpoint(self) -> Dict:
        """Load checkpoint from previous run"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        return {"last_rule": 0, "last_page": 1}

    def save_checkpoint(self, rule_number: int, page_number: int):
        """Save checkpoint for resuming"""
        checkpoint = {
            "last_rule": rule_number,
            "last_page": page_number,
            "timestamp": time.time(),
        }
        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)

    def read_pages(self, start_page: int, num_pages: int = 5) -> List[str]:
        """
        Read multiple structured pages

        Args:
            start_page: Starting page number
            num_pages: Number of pages to read

        Returns:
            List of page contents
        """
        pages = []
        for i in range(num_pages):
            page_num = start_page + i
            page_file = self.structured_pages_dir / f"page_{page_num:03d}.md"

            if not page_file.exists():
                break

            with open(page_file, 'r', encoding='utf-8') as f:
                pages.append(f.read())

        return pages

    def extract_rule(
        self,
        rule_number: int,
        start_page: int,
        max_pages: int = 10,
    ) -> RuleExtractionResult:
        """
        Extract a single rule using Claude CLI

        Args:
            rule_number: Rule number to extract (1-972)
            start_page: Page to start searching from
            max_pages: Maximum pages to read

        Returns:
            RuleExtractionResult with extracted content
        """
        try:
            # Read pages
            pages = self.read_pages(start_page, max_pages)
            if not pages:
                return RuleExtractionResult(
                    rule_number=rule_number,
                    success=False,
                    content="",
                    end_page=start_page,
                    error=f"No pages found starting from {start_page}"
                )

            # Create extraction prompt
            prompt = PromptTemplates.extract_rule(
                rule_number=rule_number,
                pages_content=pages,
                start_page=start_page,
            )

            # Create conversation
            conv = ConversationManager()
            conv.add_user_message(prompt)

            # Get response from Claude CLI
            print(f"  Calling claude CLI...", end=" ", flush=True)
            response = self.client.chat(
                messages=conv.get_messages(),
                system=PromptTemplates.SYSTEM_RULE_EXTRACTION,
                stream=False,
            )
            print("done")

            # Parse response
            lines = response.strip().split('\n', 1)
            if len(lines) < 2:
                return RuleExtractionResult(
                    rule_number=rule_number,
                    success=False,
                    content=response,
                    end_page=start_page,
                    error="Invalid response format"
                )

            # Extract end page from JSON
            try:
                metadata = json.loads(lines[0])
                end_page = metadata.get("end_page", start_page)
            except json.JSONDecodeError:
                end_page = start_page

            content = lines[1].strip() if len(lines) > 1 else response

            return RuleExtractionResult(
                rule_number=rule_number,
                success=True,
                content=content,
                end_page=end_page,
            )

        except Exception as e:
            return RuleExtractionResult(
                rule_number=rule_number,
                success=False,
                content="",
                end_page=start_page,
                error=str(e),
            )

    def save_rule(self, result: RuleExtractionResult):
        """Save extracted rule to file"""
        if not result.success:
            return

        rule_file = self.output_dir / f"rule_{result.rule_number:03d}.md"
        with open(rule_file, 'w', encoding='utf-8') as f:
            f.write(result.content)

    def process_batch(
        self,
        start_rule: int = 1,
        end_rule: int = 972,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ):
        """
        Process a batch of rules

        Args:
            start_rule: First rule to extract
            end_rule: Last rule to extract (inclusive)
            progress_callback: Optional callback function(current, total)
        """
        # Load checkpoint
        checkpoint = self.load_checkpoint()
        if checkpoint["last_rule"] > 0 and checkpoint["last_rule"] >= start_rule:
            print(f"📁 Resuming from checkpoint: Rule {checkpoint['last_rule']}")
            start_rule = checkpoint["last_rule"] + 1
            self.current_page = checkpoint["last_page"]

        total_rules = end_rule - start_rule + 1
        print(f"\n🚀 Starting extraction: Rules {start_rule}-{end_rule} ({total_rules} rules)")
        print(f"📄 Starting from page {self.current_page}")
        print(f"💰 Cost: $0 (using Claude CLI subscription)\n")

        for rule_num in range(start_rule, end_rule + 1):
            current = rule_num - start_rule + 1

            print(f"[{current}/{total_rules}] Extracting Rule § {rule_num}...", end=" ")

            # Extract rule
            result = self.extract_rule(
                rule_number=rule_num,
                start_page=self.current_page,
            )

            if result.success:
                print(f"✓ (ends at page {result.end_page})")
                self.save_rule(result)
                self.current_page = result.end_page
                self.save_checkpoint(rule_num, self.current_page)
            else:
                print(f"✗ Error: {result.error}")
                # Don't update current_page on failure

            # Progress callback
            if progress_callback:
                progress_callback(current, total_rules)

            # Small delay between calls (be nice to CLI)
            if rule_num < end_rule:
                time.sleep(1)

        print(f"\n✅ Extraction complete!")
        print(f"💰 Total cost: $0 (subscription-based)")
