#!/usr/bin/env python3
"""
Extract rules using subprocess calls to `claude` CLI.
This avoids external API calls by using the local Claude Code instance.
"""

import subprocess
import json
import yaml
from pathlib import Path
import re
import sys


class SubprocessRuleExtractor:
    def __init__(self, structured_pages_dir: Path, output_dir: Path):
        self.structured_pages_dir = structured_pages_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Get sorted list of all pages
        self.all_pages = sorted(
            self.structured_pages_dir.glob('page_*.md'),
            key=lambda p: int(p.stem.split('_')[1])
        )
        print(f"Found {len(self.all_pages)} structured pages")

    def read_pages(self, start_page: int, num_pages: int = 10) -> tuple[str, list[int]]:
        """Read multiple pages starting from start_page."""
        pages_content = []
        page_numbers = []

        for page_file in self.all_pages:
            page_num = int(page_file.stem.split('_')[1])
            if page_num < start_page:
                continue
            if page_num >= start_page + num_pages:
                break

            content = page_file.read_text()
            pages_content.append(f"=== PAGE {page_num} ===\n{content}\n")
            page_numbers.append(page_num)

        return '\n'.join(pages_content), page_numbers

    def extract_rule_with_claude(self, rule_num: int, start_page: int, max_pages: int = 10) -> tuple[str, int, list[int]]:
        """Extract a single rule using claude CLI subprocess."""
        print(f"\n📖 Extracting rule {rule_num} starting from page {start_page}...")

        # Read pages
        pages_content, page_numbers = self.read_pages(start_page, max_pages)

        # Construct prompt
        prompt = f"""Extract rule § {rule_num} from the provided pages.

Here are the pages:

{pages_content}

Instructions:
- Find and extract the COMPLETE content for rule § {rule_num}
- Include the rule header (e.g., "## § {rule_num}. Title")
- Include ALL subsections, examples, notes that belong to this rule
- Stop when you reach the next rule's header (§ {rule_num + 1})
- Some pages have combined headers like "## § 5-6" which is context, but § 5 and § 6 are separate rules with their own headers

Return ONLY a JSON object with this structure:
{{
  "rule_content": "the complete markdown content including header",
  "end_page": <page number where this rule ends>,
  "source_pages": [<list of page numbers used>],
  "notes": "any observations"
}}

Return ONLY the JSON, no other text."""

        try:
            # Call claude CLI with subprocess
            result = subprocess.run(
                ['claude', '-p', '--output-format', 'text', prompt],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                raise Exception(f"claude CLI failed: {result.stderr}")

            response_text = result.stdout

            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                raise ValueError(f"No JSON found in response: {response_text[:200]}")

            result_data = json.loads(json_match.group(0))

            print(f"   ✓ Extracted rule {rule_num}")
            print(f"   ✓ Content length: {len(result_data['rule_content'])} chars")
            print(f"   ✓ Source pages: {result_data['source_pages']}")
            print(f"   ✓ Ends on page: {result_data['end_page']}")

            return (
                result_data['rule_content'],
                result_data['end_page'],
                result_data['source_pages']
            )

        except Exception as e:
            print(f"   ❌ Error: {e}")
            raise

    def write_rule_file(self, rule_num: int, content: str, source_pages: list[int]):
        """Write a rule to its output file."""
        rule_file = self.output_dir / f"rule_{rule_num}.md"

        yaml_data = {
            'rule': f'§ {rule_num}',
            'source_pages': source_pages
        }

        with open(rule_file, 'w', encoding='utf-8') as f:
            f.write('---\n')
            f.write(yaml.dump(yaml_data, allow_unicode=True, sort_keys=False))
            f.write('---\n\n')
            f.write(content)

        print(f"   💾 Written to {rule_file}")

    def extract_all_rules(self, start_rule: int = 1, end_rule: int = 972):
        """Extract all rules sequentially."""
        print(f"\n🚀 Starting subprocess-based extraction")
        print(f"   Rules: {start_rule} to {end_rule}")
        print(f"   Output: {self.output_dir}\n")

        current_page = 1

        for rule_num in range(start_rule, end_rule + 1):
            try:
                content, end_page, source_pages = self.extract_rule_with_claude(
                    rule_num, current_page
                )
                self.write_rule_file(rule_num, content, source_pages)

                # Next rule starts where this one ended
                current_page = end_page

                # Progress indicator
                if rule_num % 10 == 0:
                    progress = (rule_num - start_rule + 1) / (end_rule - start_rule + 1) * 100
                    print(f"\n📊 Progress: {rule_num}/{end_rule} rules ({progress:.1f}%)\n")

            except Exception as e:
                print(f"   ❌ Error extracting rule {rule_num}: {e}")
                # Try to continue from next page
                current_page += 1
                if current_page > 700:
                    print(f"   ⚠️  Reached page limit, stopping")
                    break

        print(f"\n✅ Extraction complete!")
        print(f"   Processed rules {start_rule} to {rule_num}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Extract rules using claude CLI subprocess')
    parser.add_argument('--start', type=int, default=1, help='Start rule number')
    parser.add_argument('--end', type=int, default=972, help='End rule number')
    parser.add_argument('--output', type=str, default='rules_llm', help='Output directory name')

    args = parser.parse_args()

    base_dir = Path('/Users/skmnktl/Downloads/ocr')
    structured_pages_dir = base_dir / 'structured_pages'
    output_dir = base_dir / args.output

    extractor = SubprocessRuleExtractor(structured_pages_dir, output_dir)
    extractor.extract_all_rules(args.start, args.end)


if __name__ == '__main__':
    main()
