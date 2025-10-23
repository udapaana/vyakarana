#!/usr/bin/env python3
"""
Simple extraction: Each rule goes into its own numbered file (001.md - 972.md)
No organization, no chapters, no sections - just rules.
"""

import re
from pathlib import Path
import json

class SimpleRuleExtractor:
    def __init__(self):
        self.v7_path = Path('output/kales_sanskrit_grammar_v7.md')
        self.raw_pages_dir = Path('raw_pages')
        self.output_dir = Path('rules')
        self.output_dir.mkdir(exist_ok=True)

        # Store rules: {rule_num: content_string}
        self.rules = {}

    def extract_from_v7(self):
        """Extract all rules from v7"""
        print("Extracting from v7...")
        content = self.v7_path.read_text(encoding='utf-8')
        lines = content.split('\n')

        current_rule = None
        current_content = []

        for line in lines:
            # Match rule headers - multiple formats:
            # #### § 123  (standard)
            # §. 292      (with period)
            # @[§] 921    (in brackets)
            rule_match = (re.match(r'^####\s*§\s*(\d+)', line) or
                         re.match(r'^§\.\s*(\d+)', line) or
                         re.match(r'^@\[§\]\s*(\d+)', line))

            if rule_match:
                # Save previous rule
                if current_rule is not None:
                    self._save_rule(current_rule, current_content)

                # Start new rule - INCLUDE the header line
                current_rule = int(rule_match.group(1))
                current_content = [line]  # Start with the header itself
            elif current_rule is not None:
                # Collect content until next header
                if line.startswith('#'):
                    # Hit next section/chapter, save and stop
                    self._save_rule(current_rule, current_content)
                    current_rule = None
                    current_content = []
                else:
                    current_content.append(line)

        # Save last rule
        if current_rule is not None:
            self._save_rule(current_rule, current_content)

        print(f"  Extracted {len(self.rules)} rules from v7")

    def extract_from_raw_pages(self):
        """Fill gaps from raw OCR pages"""
        print("\nFilling gaps from raw pages...")

        raw_files = sorted(self.raw_pages_dir.glob('page_*.txt'))
        found_new = 0

        for page_file in raw_files:
            content = page_file.read_text(encoding='utf-8', errors='ignore')

            # Find rule markers - handle OCR variations
            for match in re.finditer(r'§\s*(\d+)', content):
                rule_num = int(match.group(1))

                # Only extract if we don't have it from v7
                if rule_num not in self.rules and 1 <= rule_num <= 972:
                    # Extract context (next ~1000 chars until next rule or end)
                    start = match.start()

                    # Find next rule marker
                    next_rule = re.search(r'§\s*\d+', content[start+10:])
                    if next_rule:
                        end = start + 10 + next_rule.start()
                    else:
                        end = min(start + 1000, len(content))

                    rule_text = content[start:end].strip()

                    # Save as raw extraction
                    self.rules[rule_num] = {
                        'content': rule_text,
                        'source': 'raw'
                    }
                    found_new += 1

        print(f"  Found {found_new} additional rules from raw pages")
        print(f"  Total rules: {len(self.rules)}")

    def _save_rule(self, rule_num, content_lines):
        """Save rule content"""
        content = '\n'.join(content_lines).strip()

        # Only save if not empty and rule number is valid
        # IMPORTANT: Keep FIRST occurrence (don't overwrite if already exists)
        if content and 1 <= rule_num <= 972 and rule_num not in self.rules:
            self.rules[rule_num] = {
                'content': content,
                'source': 'v7'
            }

    def write_files(self):
        """Write each rule to numbered file"""
        print("\nWriting rule files...")

        for rule_num in sorted(self.rules.keys()):
            rule_data = self.rules[rule_num]
            filename = f"{rule_num:03d}.md"
            filepath = self.output_dir / filename

            # Simple format: YAML front matter + content
            content = f"""---
rule: §{rule_num}
---

{rule_data['content']}
"""

            filepath.write_text(content, encoding='utf-8')

        print(f"  Wrote {len(self.rules)} files to rules/")

    def report(self):
        """Report on extraction"""
        print("\n" + "="*60)
        print("EXTRACTION REPORT")
        print("="*60)

        expected = set(range(1, 973))  # 1-972
        found = set(self.rules.keys())
        missing = sorted(expected - found)

        print(f"Expected: 972 rules")
        print(f"Found: {len(found)} rules")
        print(f"Missing: {len(missing)} rules")

        if missing:
            print(f"\nMissing rules:")
            # Group consecutive
            groups = []
            i = 0
            while i < len(missing):
                start = missing[i]
                end = start
                while i + 1 < len(missing) and missing[i + 1] == end + 1:
                    i += 1
                    end = missing[i]

                if start == end:
                    groups.append(f"§{start}")
                else:
                    groups.append(f"§{start}-§{end}")
                i += 1

            print("  " + ", ".join(groups))

        # Source breakdown
        v7_count = sum(1 for r in self.rules.values() if r['source'] == 'v7')
        raw_count = sum(1 for r in self.rules.values() if r['source'] == 'raw')

        print(f"\nSources:")
        print(f"  v7: {v7_count}")
        print(f"  raw pages: {raw_count}")

        # Save missing list
        if missing:
            missing_file = self.output_dir / 'MISSING.txt'
            missing_file.write_text('\n'.join(f"§{n}" for n in missing))
            print(f"\nMissing list saved to {missing_file}")

        return missing

    def run(self):
        """Run extraction"""
        print("="*60)
        print("SIMPLE RULE EXTRACTION")
        print("Target: 972 rules → 001.md through 972.md")
        print("="*60 + "\n")

        self.extract_from_v7()
        self.extract_from_raw_pages()
        self.write_files()
        missing = self.report()

        if not missing:
            print("\n✅ SUCCESS: All 972 rules extracted!")
        else:
            print(f"\n⚠️  {len(missing)} rules still missing - need manual extraction")

        return missing

if __name__ == '__main__':
    extractor = SimpleRuleExtractor()
    extractor.run()
