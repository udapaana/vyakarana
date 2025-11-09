"""
Sequential page-by-page rule extraction with fresh context per rule
"""

import subprocess
import json
import time
import re
from pathlib import Path
from typing import Optional, Dict
from dataclasses import dataclass


@dataclass
class ExtractionState:
    """Current extraction state"""

    current_rule: int
    current_page: int
    total_rules_extracted: int


class SequentialExtractor:
    """
    Simple sequential extractor that processes page-by-page

    Strategy:
    1. Start with Rule N at Page P
    2. Keep adding pages until rule is complete
    3. Use fresh Claude session for each rule (no context buildup)
    4. Save checkpoint after each rule
    """

    def __init__(self, structured_pages_dir: Path, output_dir: Path):
        self.structured_pages_dir = Path(structured_pages_dir)
        self.output_dir = Path(output_dir)
        self.checkpoint_file = self.output_dir / ".checkpoint.json"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_checkpoint(self) -> ExtractionState:
        """Load checkpoint or start fresh"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, "r") as f:
                data = json.load(f)
                return ExtractionState(
                    current_rule=data.get("current_rule", 1),
                    current_page=data.get("current_page", 1),
                    total_rules_extracted=data.get("total_rules_extracted", 0),
                )
        return ExtractionState(current_rule=1, current_page=1, total_rules_extracted=0)

    def save_checkpoint(self, state: ExtractionState):
        """Save checkpoint"""
        with open(self.checkpoint_file, "w") as f:
            json.dump(
                {
                    "current_rule": state.current_rule,
                    "current_page": state.current_page,
                    "total_rules_extracted": state.total_rules_extracted,
                    "timestamp": time.time(),
                },
                f,
                indent=2,
            )

    def read_pages(self, start_page: int, count: int = 10) -> list[str]:
        """Read consecutive pages"""
        pages = []
        for i in range(count):
            page_num = start_page + i
            page_file = self.structured_pages_dir / f"page_{page_num:03d}.md"
            if not page_file.exists():
                break
            with open(page_file, "r", encoding="utf-8") as f:
                pages.append(f.read())
        return pages

    def extract_rule(self, rule_num: int, start_page: int) -> tuple[str, int]:
        """
        Extract a single rule using fresh Claude session

        Returns: (rule_content, end_page)
        """
        # Read up to 10 pages (most rules are 1-3 pages)
        pages = self.read_pages(start_page, count=10)
        if not pages:
            raise RuntimeError(f"No pages found starting from {start_page}")

        # Build prompt
        pages_text = "\n\n---PAGE_BREAK---\n\n".join(
            f"=== PAGE {start_page + i} ===\n{content}"
            for i, content in enumerate(pages)
        )

        system_prompt = """You are extracting Sanskrit grammar rules from OCR'd pages.

Extract ONLY rule § {rule_num}. Include everything that belongs to this rule.

Output format:
Line 1: {{"end_page": N}}
Lines 2+: Complete markdown content for the rule

Stop when you reach the next rule or section.""".format(rule_num=rule_num)

        full_prompt = f"""Extract rule § {rule_num} from the following pages.

PAGES:
{pages_text}

INSTRUCTIONS:
1. Find where § {rule_num} starts (may be in a combined header like "§ {rule_num - 1}-{rule_num}")
2. Extract ALL content for § {rule_num}:
   - Rule title and number
   - Complete explanation
   - All examples (Devanagari + IAST)
   - Footnotes and references
3. Determine where § {rule_num} ends
4. First line output: {{"end_page": N}}
5. Rest: Complete markdown with YAML front matter

Begin extraction:"""

        # Call Claude CLI with fresh session (no --continue, no --resume)
        import os

        env = os.environ.copy()
        env.pop("ANTHROPIC_API_KEY", None)  # Use browser auth

        result = subprocess.run(
            ["claude", "--print", "--system-prompt", system_prompt],
            input=full_prompt,
            capture_output=True,
            text=True,
            timeout=300,
            env=env,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Claude CLI error: {result.stderr}")

        response = result.stdout.strip()

        # Parse response
        lines = response.split("\n", 1)
        if len(lines) < 2:
            raise RuntimeError(f"Invalid response format")

        # Extract end_page from JSON
        try:
            # Try to find JSON in first few lines
            json_match = re.search(r'\{.*"end_page".*:.*(\d+).*\}', lines[0])
            if json_match:
                metadata = json.loads(json_match.group(0))
                end_page = metadata.get("end_page", start_page + 1)
            else:
                end_page = start_page + 1
        except:
            end_page = start_page + 1

        content = lines[1] if len(lines) > 1 else response

        return content.strip(), end_page

    def extract_all(self, start_rule: int = 1, end_rule: int = 972):
        """Extract all rules sequentially"""
        state = self.load_checkpoint()

        # Resume from checkpoint if applicable
        if state.current_rule > start_rule:
            print(
                f"📁 Resuming from checkpoint: Rule {state.current_rule}, Page {state.current_page}"
            )
            start_rule = state.current_rule
        else:
            state = ExtractionState(start_rule, 1, 0)

        print(f"\n🚀 Sequential Extraction: Rules {start_rule}-{end_rule}")
        print(f"📄 Starting at page {state.current_page}")
        print(f"💰 Cost: $0 (using Claude CLI with browser auth)")
        print(f"♻️  Fresh context per rule (no memory buildup)\n")

        for rule_num in range(start_rule, end_rule + 1):
            try:
                print(
                    f"[{rule_num}/{end_rule}] Extracting Rule § {rule_num} (from page {state.current_page})...",
                    end=" ",
                    flush=True,
                )

                # Extract rule with fresh context
                content, end_page = self.extract_rule(rule_num, state.current_page)

                # Save rule
                rule_file = self.output_dir / f"rule_{rule_num:03d}.md"
                with open(rule_file, "w", encoding="utf-8") as f:
                    f.write(content)

                print(f"✓ (ends at page {end_page})")

                # Update state
                state.current_rule = rule_num + 1
                state.current_page = end_page
                state.total_rules_extracted += 1

                # Save checkpoint
                self.save_checkpoint(state)

                # Small delay between rules
                time.sleep(1)

            except Exception as e:
                print(f"✗ Error: {e}")
                # Save checkpoint even on error
                self.save_checkpoint(state)
                # Continue to next rule (optional: could break here)
                state.current_rule = rule_num + 1

        print(f"\n✅ Extraction complete!")
        print(f"📊 Extracted {state.total_rules_extracted} rules")
        print(f"💰 Total cost: $0 (subscription-based)")


def main():
    import sys

    output_dir = sys.argv[1] if len(sys.argv) > 1 else "phase3_rules"

    extractor = SequentialExtractor(
        structured_pages_dir=Path("phase2_structured"), output_dir=Path(output_dir)
    )

    extractor.extract_all(start_rule=1, end_rule=972)


if __name__ == "__main__":
    main()
