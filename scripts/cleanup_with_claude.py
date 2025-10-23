#!/usr/bin/env python3
"""
Process each rule through Claude for OCR corrections, typo fixes, and markdown spec conformance.
Processes rules in batches to manage API calls efficiently.
"""

import anthropic
import os
from pathlib import Path
import time
import json

# Markdown spec for reference
MARKDOWN_SPEC = """
# Markdown Formatting Specification

1. **YAML Front Matter**: Each file must start with:
   ---
   rule: §N
   ---

2. **Rule Header**: Use #### for rule headers:
   #### § N. [Rule title/description]

3. **IAST Transliteration**: Sanskrit terms should be in IAST notation wrapped in @[...]:
   @[saṃskṛta], @[devanāgarī], etc.

4. **Devanagari**: Keep Devanagari script as-is (no changes needed)

5. **Lists**: Use proper markdown lists (- or 1. 2. 3.)

6. **Tables**: Use markdown table format where appropriate

7. **Footnotes/References**: Use superscript or footnote markers

8. **Formatting**:
   - Bold: **text**
   - Italic: *text* (for emphasis)
   - Code/Technical: `text`

9. **Spacing**: Proper spacing around headers, paragraphs, and lists
"""

CLEANUP_PROMPT = """You are cleaning up an OCR-extracted rule from Kale's Sanskrit Grammar.

Your tasks:
1. Fix OCR errors (common: ० vs 0, १ vs 1, misread characters)
2. Fix typos and grammatical errors
3. Ensure proper markdown formatting per the spec
4. Standardize IAST transliteration in @[...] notation
5. Keep Devanagari script intact
6. Fix spacing and formatting issues
7. Ensure the rule header starts with #### § N.

IMPORTANT:
- Do NOT change the meaning or content
- Do NOT translate anything
- Do NOT remove content
- Keep all examples, notes, and references
- Maintain the YAML front matter exactly as is

Return ONLY the cleaned markdown content (including YAML front matter).
"""

class RuleCleanup:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.rules_dir = Path('rules')
        self.output_dir = Path('rules_cleaned')
        self.output_dir.mkdir(exist_ok=True)

        # Track progress
        self.progress_file = Path('cleanup_progress.json')
        self.load_progress()

    def load_progress(self):
        """Load cleanup progress"""
        if self.progress_file.exists():
            with open(self.progress_file) as f:
                self.progress = json.load(f)
        else:
            self.progress = {
                'completed': [],
                'failed': [],
                'last_processed': 0
            }

    def save_progress(self):
        """Save cleanup progress"""
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)

    def cleanup_rule(self, rule_num):
        """Clean up a single rule using Claude"""
        filename = f"{rule_num:03d}.md"
        input_path = self.rules_dir / filename
        output_path = self.output_dir / filename

        # Skip if already completed
        if rule_num in self.progress['completed']:
            print(f"  §{rule_num} - already completed, skipping")
            return True

        # Read original
        if not input_path.exists():
            print(f"  §{rule_num} - file not found")
            return False

        original_content = input_path.read_text(encoding='utf-8')

        # Skip placeholder files
        if 'DOES NOT EXIST IN ORIGINAL' in original_content:
            output_path.write_text(original_content, encoding='utf-8')
            self.progress['completed'].append(rule_num)
            print(f"  §{rule_num} - placeholder, copied as-is")
            return True

        try:
            # Call Claude for cleanup
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": f"{CLEANUP_PROMPT}\n\nMarkdown Spec:\n{MARKDOWN_SPEC}\n\nRule to clean:\n\n{original_content}"
                    }
                ]
            )

            cleaned_content = message.content[0].text

            # Save cleaned version
            output_path.write_text(cleaned_content, encoding='utf-8')

            # Update progress
            self.progress['completed'].append(rule_num)
            self.progress['last_processed'] = rule_num
            self.save_progress()

            print(f"  §{rule_num} - cleaned ✓")
            return True

        except Exception as e:
            print(f"  §{rule_num} - ERROR: {e}")
            self.progress['failed'].append(rule_num)
            self.save_progress()
            return False

    def cleanup_batch(self, start=1, end=972, delay=1.0):
        """Clean up a batch of rules"""
        print("="*60)
        print("CLAUDE CLEANUP - OCR CORRECTIONS & FORMATTING")
        print("="*60)
        print(f"\nProcessing rules §{start} to §{end}")
        print(f"Delay between calls: {delay}s\n")

        success_count = 0
        fail_count = 0

        for rule_num in range(start, end + 1):
            if self.cleanup_rule(rule_num):
                success_count += 1
            else:
                fail_count += 1

            # Rate limiting
            if rule_num < end:
                time.sleep(delay)

        print(f"\n{'='*60}")
        print(f"BATCH COMPLETE")
        print(f"{'='*60}")
        print(f"Successful: {success_count}")
        print(f"Failed: {fail_count}")
        print(f"Total completed so far: {len(self.progress['completed'])}/966")

        return success_count, fail_count

    def cleanup_all(self, batch_size=50, delay=1.0):
        """Clean up all rules in batches"""
        total_rules = 972

        for batch_start in range(1, total_rules + 1, batch_size):
            batch_end = min(batch_start + batch_size - 1, total_rules)

            print(f"\n{'='*60}")
            print(f"BATCH: Rules {batch_start}-{batch_end}")
            print(f"{'='*60}\n")

            self.cleanup_batch(batch_start, batch_end, delay)

            # Longer pause between batches
            if batch_end < total_rules:
                print(f"\nPausing 5 seconds before next batch...\n")
                time.sleep(5)

if __name__ == '__main__':
    import sys

    # Check for API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        print("Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)

    cleaner = RuleCleanup()

    # Allow command-line arguments for batch processing
    if len(sys.argv) > 1:
        if sys.argv[1] == 'resume':
            start = cleaner.progress['last_processed'] + 1
            cleaner.cleanup_batch(start, 972)
        elif sys.argv[1] == 'range':
            start = int(sys.argv[2])
            end = int(sys.argv[3])
            cleaner.cleanup_batch(start, end)
        else:
            print("Usage:")
            print("  python cleanup_with_claude.py          # Process all rules")
            print("  python cleanup_with_claude.py resume   # Resume from last processed")
            print("  python cleanup_with_claude.py range START END  # Process specific range")
    else:
        # Process all
        cleaner.cleanup_all(batch_size=50, delay=1.0)
