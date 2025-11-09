"""
Parallel-safe rule extractor

Features:
- Start from any page, finds first rule after that point
- Skips already-extracted rules
- Terminates when hitting completed rule
- Logs errors with start pages for retry
"""

import subprocess
import json
import time
import re
from pathlib import Path
from typing import Optional, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RuleInfo:
    """Information about a rule"""

    rule_num: int
    start_page: int
    end_page: Optional[int] = None
    error: Optional[str] = None


class ParallelExtractor:
    """
    Parallel-safe extractor for concurrent rule extraction

    Key features:
    - Start from any page
    - Auto-detect first rule on/after that page
    - Skip already-extracted rules
    - Stop when hitting completed rules
    - Log errors with start pages
    """

    def __init__(
        self, structured_pages_dir: Path, output_dir: Path, status_file: Path = None
    ):
        self.structured_pages_dir = Path(structured_pages_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Status tracking (similar to Phase 2)
        self.status_file = status_file or Path("data/phase3_extraction_status.json")
        self.status_file.parent.mkdir(parents=True, exist_ok=True)

        # Legacy logs (keep for compatibility)
        self.error_log = self.output_dir / "extraction_errors.json"
        self.progress_log = self.output_dir / "extraction_progress.json"

        # Initialize or load status
        self._init_status()

    def _init_status(self):
        """Initialize or load extraction status"""
        if self.status_file.exists():
            with open(self.status_file, "r") as f:
                self.status = json.load(f)
        else:
            self.status = {
                "extracted_rules": [],
                "errors": {},
                "last_updated": None,
                "total_rules": 972,
                "total_extracted": 0,
                "total_errors": 0,
            }
            self._save_status()

    def _save_status(self):
        """Save current status to file"""
        from datetime import datetime

        self.status["last_updated"] = datetime.utcnow().isoformat()
        self.status["total_extracted"] = len(self.status["extracted_rules"])
        self.status["total_errors"] = len(self.status["errors"])

        with open(self.status_file, "w") as f:
            json.dump(self.status, f, indent=2)

    def mark_rule_extracted(self, rule_num: int, page_start: int, page_end: int):
        """Mark a rule as successfully extracted"""
        rule_id = f"rule_{rule_num:03d}"
        if rule_id not in self.status["extracted_rules"]:
            self.status["extracted_rules"].append(rule_id)

        # Remove from errors if it was there
        if str(rule_num) in self.status["errors"]:
            del self.status["errors"][str(rule_num)]

        self._save_status()

    def mark_rule_error(self, rule_num: int, error_msg: str, page_start: int):
        """Mark a rule as having an extraction error"""
        from datetime import datetime

        self.status["errors"][str(rule_num)] = {
            "error": error_msg,
            "page_start": page_start,
            "timestamp": datetime.utcnow().isoformat(),
            "retry_count": self.status["errors"]
            .get(str(rule_num), {})
            .get("retry_count", 0)
            + 1,
        }
        self._save_status()

    def is_rule_extracted(self, rule_num: int) -> bool:
        """Check if rule is already successfully extracted"""
        return f"rule_{rule_num:03d}" in self.status["extracted_rules"]

    def get_errored_rules(self) -> list:
        """Get list of rules that had errors"""
        return [int(r) for r in self.status["errors"].keys()]

    def find_first_rule_on_page(self, page_num: int) -> Optional[int]:
        """
        Find the first rule number mentioned on or after this page

        Returns: rule number or None
        """
        # Read page and check YAML front matter for rule number
        for offset in range(10):  # Check up to 10 pages ahead
            page_file = self.structured_pages_dir / f"page_{page_num + offset:03d}.md"
            if not page_file.exists():
                continue

            with open(page_file, "r", encoding="utf-8") as f:
                content = f.read(2000)  # Read first 2000 chars

            # Look for rule: "§ N" in YAML
            match = re.search(r'rule:\s*["\']?\s*§\s*(\d+)', content)
            if match:
                return int(match.group(1))

            # Look for rule in content
            match = re.search(r"##\s*§\s*(\d+)", content)
            if match:
                return int(match.group(1))

        return None

    def rule_exists(self, rule_num: int) -> bool:
        """Check if rule file already exists"""
        rule_file = self.output_dir / f"rule_{rule_num:03d}.md"
        return rule_file.exists() and rule_file.stat().st_size > 100

    def validate_rule_schema(self, rule_num: int, content: str) -> tuple[bool, str]:
        """
        Validate that extracted content follows the required schema

        Returns: (is_valid, error_message)
        """
        import yaml

        # Extract YAML frontmatter
        if not content.strip().startswith("---"):
            return False, "Missing YAML frontmatter"

        try:
            parts = content.split("---", 2)
            if len(parts) < 3:
                return False, "Invalid YAML structure"

            yaml_str = parts[1]
            yaml_data = yaml.safe_load(yaml_str)

            if not yaml_data:
                return False, "Empty YAML frontmatter"

            # Check required fields
            required = [
                "rule_number",
                "rule_id",
                "title",
                "chapter",
                "section",
                "page_start",
                "page_end",
                "topics",
                "word_index",
                "source_pages",
            ]

            missing = [f for f in required if f not in yaml_data]
            if missing:
                return False, f"Missing: {', '.join(missing)}"

            # Validate rule_number matches
            if yaml_data.get("rule_number") != rule_num:
                return (
                    False,
                    f"rule_number mismatch: {yaml_data.get('rule_number')} != {rule_num}",
                )

            # Validate types
            if not isinstance(yaml_data.get("topics"), list) or not yaml_data.get(
                "topics"
            ):
                return False, "topics must be non-empty list"

            if not isinstance(yaml_data.get("source_pages"), list) or not yaml_data.get(
                "source_pages"
            ):
                return False, "source_pages must be non-empty list"

            return True, ""

        except Exception as e:
            return False, f"Schema error: {str(e)}"

    def validate_extracted_content(self, rule_num: int, content: str) -> bool:
        """
        Validate that extracted content is actually the rule, not an error message

        Returns: True if valid, False if invalid
        """
        # First: Schema validation
        schema_valid, schema_error = self.validate_rule_schema(rule_num, content)
        if not schema_valid:
            print(f"\n  ⚠️  Schema validation failed: {schema_error}")
            return False

        # Check for error messages
        error_phrases = [
            "NOT present",
            "not found",
            "not included",
            "missing from",
            "not appear",
            "Rule § " + str(rule_num) + " is not",
            "§ " + str(rule_num) + " is not",
        ]

        content_lower = content[:1000].lower()
        for phrase in error_phrases:
            if phrase.lower() in content_lower:
                return False

        # Check that the rule number appears in content
        # Look for "§ {rule_num}" in headings or YAML
        rule_patterns = [
            f"§ {rule_num}",
            f"§{rule_num}",
            f'rule: "§ {rule_num}"',
            f"rule: '§ {rule_num}'",
            f"## § {rule_num}",
        ]

        has_rule_number = any(pattern in content[:2000] for pattern in rule_patterns)

        if not has_rule_number:
            return False

        # Check minimum content length (should have substantial content)
        if len(content.strip()) < 100:
            return False

        # Check for YAML frontmatter (proper format)
        if not content.strip().startswith("---"):
            return False

        return True

    def log_error(self, rule_num: int, start_page: int, error: str):
        """Log extraction error with start page"""
        errors = []
        if self.error_log.exists():
            with open(self.error_log, "r") as f:
                errors = json.load(f)

        errors.append(
            {
                "rule": rule_num,
                "start_page": start_page,
                "error": error,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        with open(self.error_log, "w") as f:
            json.dump(errors, f, indent=2)

    def log_progress(self, rule_num: int, start_page: int, end_page: int):
        """Log successful extraction"""
        progress = {}
        if self.progress_log.exists():
            with open(self.progress_log, "r") as f:
                progress = json.load(f)

        progress[str(rule_num)] = {
            "start_page": start_page,
            "end_page": end_page,
            "timestamp": datetime.utcnow().isoformat(),
        }

        with open(self.progress_log, "w") as f:
            json.dump(progress, f, indent=2)

    def read_pages(self, start_page: int, count: int = 10) -> list[str]:
        """Read consecutive pages, including those with letter suffixes (013a, 013b)"""
        pages = []
        page_num = start_page
        pages_read = 0

        while pages_read < count:
            # Try base page first
            page_file = self.structured_pages_dir / f"page_{page_num:03d}.md"

            if page_file.exists():
                with open(page_file, "r", encoding="utf-8") as f:
                    pages.append(f.read())
                pages_read += 1

                # Check for suffixed pages (013a, 013b, etc.)
                for suffix in "abcdefghij":
                    suffixed_file = (
                        self.structured_pages_dir / f"page_{page_num:03d}{suffix}.md"
                    )
                    if suffixed_file.exists() and pages_read < count:
                        with open(suffixed_file, "r", encoding="utf-8") as f:
                            pages.append(f.read())
                        pages_read += 1
                    else:
                        break  # No more suffixes for this page number

                page_num += 1
            else:
                # No base page found, stop reading
                break

        return pages

    def check_page_continuation(self, page_num: int) -> Optional[str]:
        """
        Check if a page has continuation marker

        Returns: next page name if continues, None otherwise
        """
        import yaml

        page_file = self.structured_pages_dir / f"page_{page_num:03d}.md"
        if not page_file.exists():
            return None

        with open(page_file) as f:
            content = f.read()

        # Extract YAML frontmatter
        if not content.startswith("---"):
            return None

        parts = content.split("---", 2)
        if len(parts) < 3:
            return None

        try:
            yaml_data = yaml.safe_load(parts[1])
            return yaml_data.get("continues_to")
        except:
            return None

    def validate_rule_completeness(
        self, rule_num: int, content: str, start_page: int
    ) -> Tuple[bool, str]:
        """
        Validate that extracted rule is complete (not cut off at page boundary)

        Returns: (is_complete, reason)
        """
        import yaml

        # Extract YAML from content
        if not content.startswith("---"):
            return False, "Missing YAML frontmatter"

        parts = content.split("---", 2)
        if len(parts) < 3:
            return False, "Malformed YAML frontmatter"

        try:
            yaml_data = yaml.safe_load(parts[1])
            page_start = yaml_data.get("page_start", start_page)
            page_end = yaml_data.get("page_end", start_page)
            source_pages = yaml_data.get("source_pages", [])
        except:
            return False, "Failed to parse YAML"

        # Check 1: If start page has continuation, we should have used multiple pages
        continues_to = self.check_page_continuation(page_start)

        if continues_to and page_start == page_end:
            # The source page continues, but we only extracted from one page
            return (
                False,
                f"Page {page_start} continues to {continues_to} but extraction stopped at page {page_end}",
            )

        if continues_to and len(source_pages) == 1:
            return (
                False,
                f"Page {page_start} continues to {continues_to} but only 1 source_page listed",
            )

        # Check 2: Look for incomplete sentences at the end
        content_text = parts[2] if len(parts) > 2 else ""
        content_end = content_text.strip()[-200:] if content_text else ""

        incomplete_patterns = [
            (r"\bis\s*\[?\^?\d*\]?\s*$", "ends with 'is'"),
            (r"\bare\s*\[?\^?\d*\]?\s*$", "ends with 'are'"),
            (r"\bthe\s*\[?\^?\d*\]?\s*$", "ends with 'the'"),
            (r"\band\s*\[?\^?\d*\]?\s*$", "ends with 'and'"),
            (r"\bor\s*\[?\^?\d*\]?\s*$", "ends with 'or'"),
            (r"\bof\s*\[?\^?\d*\]?\s*$", "ends with 'of'"),
            (r"\bto\s*\[?\^?\d*\]?\s*$", "ends with 'to'"),
            (r"\ba\s*\[?\^?\d*\]?\s*$", "ends with 'a'"),
        ]

        for pattern, desc in incomplete_patterns:
            if re.search(pattern, content_end, re.IGNORECASE):
                return False, f"Incomplete sentence: {desc}"

        return True, ""

    def extract_rule(self, rule_num: int, start_page: int) -> Tuple[str, int]:
        """
        Extract a single rule using fresh Claude session

        Returns: (rule_content, end_page)
        """
        # Read up to 10 pages
        pages = self.read_pages(start_page, count=10)
        if not pages:
            raise RuntimeError(f"No pages found starting from {start_page}")

        # Build prompt
        pages_text = "\n\n---PAGE_BREAK---\n\n".join(
            f"=== PAGE {start_page + i} ===\n{content}"
            for i, content in enumerate(pages)
        )

        system_prompt = f"""You are extracting Sanskrit grammar rules from OCR'd pages.

Extract ONLY rule § {rule_num} following this EXACT schema:

OUTPUT FORMAT:
Line 1: {{"end_page": N}}
Lines 2+: Structured markdown with YAML frontmatter

REQUIRED YAML FRONTMATTER:
---
rule_number: {rule_num}
rule_id: "§ {rule_num}"
title: "Rule Title Here"
chapter: "Chapter Name"
section: "section-slug"
page_start: N or "Na"
page_end: N or "Na"
topics: [topic1, topic2, ...]
word_index: [sanskrit-term-1, sanskrit-term-2, ...]
panini_refs: []
cross_refs: []
examples_count: 0
has_table: true/false
has_footnotes: true/false
source_pages: ["page_NNN.md"]
---

REQUIRED CONTENT FORMAT:
## § {rule_num}. Rule Title

Main explanation text...

@note[type=note]: Notes if present
@example[sanskrit]{{Sanskrit}} @[IAST]: Translation

VALIDATION:
- Must include § {rule_num} in heading
- Must have YAML frontmatter
- Must have substantive content (>100 chars)
- Must use @deva[] for Devanagari, @[] for IAST
- Extract COMPLETE rule: finish all sentences even if next rule starts on same page
- Stop when you encounter the heading for § {rule_num + 1}"""

        full_prompt = f"""Extract rule § {rule_num} from the following pages.

PAGES:
{pages_text}

CRITICAL INSTRUCTIONS:
1. Find where § {rule_num} starts (may be in combined header like "§ {rule_num - 1}-{rule_num}")

2. Extract ALL content for § {rule_num} including:
   - Rule title and number
   - Complete explanation (DO NOT CUT OFF mid-sentence)
   - All subsections (a), (b), (c), etc.
   - All examples (Devanagari + IAST)
   - All footnotes [^1], [^2], etc.
   - Everything until you see the HEADING "## § {rule_num + 1}" (not just page YAML metadata)

3. IGNORE PAGE YAML METADATA for determining where rules end:
   - A page may be marked "rule: § {rule_num + 1}" in YAML but still contain continuation of § {rule_num}
   - Only stop when you see the actual HEADING "## § {rule_num + 1}. [Title]"
   - Complete ALL sentences before that heading

4. DETECT CONTINUATION across pages:
   - Check if "continues_from" or "continues_to" in page YAML
   - Look for incomplete sentences at page boundaries
   - If a sentence is incomplete, read the next page content to complete it

5. Determine ACTUAL end page where § {rule_num} finishes

6. Output format:
   Line 1: {{"end_page": N, "source_pages": ["page_XXX.md", "page_YYY.md"]}}
   Rest: Complete markdown with YAML front matter

EXAMPLE of continuation detection:
  Page 11 YAML: "rule: § 3"
  Page 11 ends: "udātta is"
  Page 12 YAML: "rule: § 4" ← IGNORE THIS
  Page 12 content starts: "that which proceeds from..." ← This completes § 3's sentence
  Page 12 later has: "## § 4. The Consonants" ← NOW stop
  → Extract everything from page 11 + page 12 up to the § 4 heading

Begin extraction:"""

        # Call Claude CLI with fresh session
        import os

        env = os.environ.copy()
        env.pop("ANTHROPIC_API_KEY", None)  # Use browser auth

        # Use full path to claude CLI
        claude_path = "/etc/profiles/per-user/skmnktl/bin/claude"

        result = subprocess.run(
            [claude_path, "--print", "--system-prompt", system_prompt],
            input=full_prompt,
            capture_output=True,
            text=True,
            timeout=300,
            env=env,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Claude CLI error: {result.stderr}")

        response = result.stdout.strip()

        # DEBUG: Save raw response for first few rules
        if rule_num <= 5:
            debug_file = self.output_dir / f"debug_response_rule_{rule_num:03d}.txt"
            with open(debug_file, "w", encoding="utf-8") as f:
                f.write(f"=== RAW RESPONSE FOR RULE {rule_num} ===\n\n")
                f.write(response)
                f.write(f"\n\n=== END RESPONSE ===\n")

        # Parse response - strip JSON metadata and extract content
        end_page = start_page + 1
        source_pages = []
        content = response

        lines = response.split("\n")

        # Look for JSON metadata in entire response (not just first 5 lines)
        json_line_idx = None
        for i, line in enumerate(lines):
            json_match = re.search(r'\{"end_page":\s*\d+', line)
            if json_match:
                try:
                    # Extract full JSON from this line
                    full_json = re.search(r"\{[^}]+\}", line)
                    if full_json:
                        metadata = json.loads(full_json.group(0))
                        end_page = metadata.get("end_page", start_page + 1)
                        source_pages = metadata.get("source_pages", [])
                        json_line_idx = i
                        break
                except:
                    pass

        # Find where YAML frontmatter starts (look for "---")
        yaml_start_idx = None
        for i, line in enumerate(lines):
            if line.strip() == "---":
                yaml_start_idx = i
                break

        # Content starts at YAML frontmatter, not after JSON
        if yaml_start_idx is not None:
            content = "\n".join(lines[yaml_start_idx:]).strip()
        else:
            # Fallback: if no YAML marker found, use everything after JSON (if found)
            content_start = json_line_idx + 1 if json_line_idx is not None else 0
            content = "\n".join(lines[content_start:]).strip()

        # Remove any markdown code fences around the entire content
        if content.startswith("```") and content.endswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1]).strip()

        return content, end_page

    def extract_from_page(self, start_page: int, max_rules: int = 972):
        """
        Extract rules starting from a specific page

        Strategy:
        1. Find first rule on/after start_page
        2. Extract rules sequentially
        3. Skip already-extracted rules
        4. Stop when hitting completed rule
        """
        print(f"\n🔍 Finding first rule on/after page {start_page}...")

        # Find first rule
        first_rule = self.find_first_rule_on_page(start_page)
        if not first_rule:
            print(f"❌ No rule found on/after page {start_page}")
            return

        print(f"✓ Found Rule § {first_rule} starting at page {start_page}")

        current_page = start_page
        current_rule = first_rule
        rules_extracted = 0
        rules_skipped = 0

        print(f"\n🚀 Starting extraction from Rule § {current_rule}")
        print(f"📄 Current page: {current_page}")
        print(f"♻️  Fresh context per rule\n")

        while current_rule <= max_rules:
            # Check if rule already extracted (via status tracking)
            if self.is_rule_extracted(current_rule):
                print(
                    f"[{current_rule}] Rule § {current_rule} already extracted, stopping."
                )
                rules_skipped += 1
                break

            try:
                print(
                    f"[{current_rule}] Extracting Rule § {current_rule} (from page {current_page})...",
                    end=" ",
                    flush=True,
                )

                # Extract rule
                content, end_page = self.extract_rule(current_rule, current_page)

                # VALIDATION: Only save if content is valid
                if not self.validate_extracted_content(current_rule, content):
                    raise RuntimeError(
                        f"Validation failed - invalid content for § {current_rule}"
                    )

                # Save rule
                rule_file = self.output_dir / f"rule_{current_rule:03d}.md"
                with open(rule_file, "w", encoding="utf-8") as f:
                    f.write(content)

                print(f"✓ (ends at page {end_page})")

                # Mark as extracted in status
                self.mark_rule_extracted(current_rule, current_page, end_page)

                # Log progress (legacy)
                self.log_progress(current_rule, current_page, end_page)

                # Update for next iteration
                current_page = end_page
                current_rule += 1
                rules_extracted += 1

                # Small delay
                time.sleep(1)

            except Exception as e:
                error_msg = str(e)
                print(f"✗ Error: {error_msg}")

                # Mark error in status
                self.mark_rule_error(current_rule, error_msg, current_page)

                # Log error with start page (legacy)
                self.log_error(current_rule, current_page, error_msg)

                # Move to next rule (increment page by 1 to avoid infinite loop)
                current_rule += 1
                current_page += 1

        print(f"\n✅ Extraction complete from this starting point!")
        print(f"📊 Extracted: {rules_extracted} rules")
        print(f"⏭️  Skipped: {rules_skipped} rules (already existed)")

        # Show error summary
        if self.error_log.exists():
            with open(self.error_log, "r") as f:
                errors = json.load(f)
                if errors:
                    print(f"\n⚠️  Errors logged: {len(errors)}")
                    print(f"   Check: {self.error_log}")


def main():
    import sys

    if len(sys.argv) < 2:
        print(
            "Usage: python -m scripts.ai.parallel_extractor <start_page> [output_dir]"
        )
        print("\nExamples:")
        print("  python -m scripts.ai.parallel_extractor 1")
        print("  python -m scripts.ai.parallel_extractor 200")
        print("  python -m scripts.ai.parallel_extractor 400 rules")
        sys.exit(1)

    start_page = int(sys.argv[1])
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "phase3_rules"

    extractor = ParallelExtractor(
        structured_pages_dir=Path("phase2_structured"), output_dir=Path(output_dir)
    )

    extractor.extract_from_page(start_page=start_page)


if __name__ == "__main__":
    main()
