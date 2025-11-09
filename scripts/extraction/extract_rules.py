#!/usr/bin/env python3
"""
Extract individual rules from structured pages into separate rule files.

This script:
1. Scans all structured_pages/page_*.md files
2. Extracts content for each § rule number
3. Combines multi-page rules
4. Creates individual rules/rule_NNN.md files
5. Preserves YAML metadata and content
"""

import re
from pathlib import Path
from collections import defaultdict
import yaml

class RuleExtractor:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.structured_pages = self.repo_path / "structured_pages"
        self.rules_output = self.repo_path / "rules"
        self.appendices_output = self.repo_path / "appendices"
        self.rules_output.mkdir(exist_ok=True)
        self.appendices_output.mkdir(exist_ok=True)

        # Map rule numbers to pages
        self.rule_to_pages = defaultdict(list)  # "123" -> [page_123.md, page_124.md]
        self.appendix_to_pages = defaultdict(list)  # Appendix rules

    def scan_pages(self):
        """Scan all pages and build rule-to-page mapping."""
        print("📖 Scanning structured pages...")

        for md_file in sorted(self.structured_pages.glob("page_*.md")):
            page_num = int(md_file.stem.split('_')[1])
            if page_num > 726:  # Skip library metadata
                continue

            content = md_file.read_text()

            # Extract YAML front matter
            yaml_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if not yaml_match:
                continue

            try:
                yaml_text = yaml_match.group(1)
                # First try normal parsing
                try:
                    metadata = yaml.safe_load(yaml_text)
                except yaml.YAMLError:
                    # If it fails, try fixing @ symbols in arrays only
                    # Only fix unquoted @[...] in array contexts like topics: [...]
                    lines = yaml_text.split('\n')
                    fixed_lines = []
                    for line in lines:
                        # Check if this line has an array with unquoted @[
                        if ': [' in line and '@[' in line and '"@[' not in line:
                            # Quote unquoted @[...] patterns
                            line = re.sub(r'(?<=[,\s\[])(@\[[^\]]+\])(?=[,\s\]])', r'"\1"', line)
                        fixed_lines.append(line)
                    yaml_text_fixed = '\n'.join(fixed_lines)
                    metadata = yaml.safe_load(yaml_text_fixed)
            except:
                print(f"  ⚠️  Failed to parse YAML for page {page_num}")
                continue

            # Get rule number and chapter from metadata
            # Handle 'rule', 'rule_range', and 'rules' (plural) fields
            rule = metadata.get('rule', metadata.get('rule_range', metadata.get('rules', '')))
            chapter = metadata.get('chapter', '')

            if not rule:
                continue

            # Handle different rule formats
            rule_nums = []

            # If rule is a list: [§ 20, § 21] or [558, 559, 560]
            if isinstance(rule, list):
                for r in rule:
                    # Handle both strings and integers
                    if isinstance(r, int):
                        rule_nums.append(str(r))
                    else:
                        rule_clean = re.sub(r'§\s*', '', str(r)).strip()
                        if rule_clean:
                            rule_nums.append(rule_clean)
            # If rule is a string: "§ 123" or "§ 123-125"
            else:
                rule_clean = re.sub(r'§\s*', '', str(rule)).strip()
                if rule_clean:
                    rule_nums.append(rule_clean)

            # Check if this is an appendix page
            is_appendix = ('appendix' in str(chapter).lower() or
                          'prosody' in str(chapter).lower() or
                          page_num >= 695)  # Appendix starts around page 695

            # Add each rule number to the mapping
            for rule_num in rule_nums:
                if is_appendix:
                    self.appendix_to_pages[rule_num].append(md_file)
                else:
                    self.rule_to_pages[rule_num].append(md_file)

        print(f"   Found {len(self.rule_to_pages)} main grammar rules across {sum(len(v) for v in self.rule_to_pages.values())} pages")
        if self.appendix_to_pages:
            print(f"   Found {len(self.appendix_to_pages)} appendix sections across {sum(len(v) for v in self.appendix_to_pages.values())} pages")
        return self.rule_to_pages

    def clean_rule_content(self, content: str) -> str:
        """Remove structural headers (book title, chapter headers) from rule content.

        Keep only the actual rule section (starting with ## § N) and everything after.
        """
        lines = content.split('\n')
        cleaned_lines = []
        inside_rule = False

        for line in lines:
            # Detect rule section header: ## § 1. or ## § 16-19.
            if re.match(r'^##\s*§\s*\d+', line):
                inside_rule = True

            # Skip structural headers before the rule starts
            if not inside_rule:
                # Skip these patterns:
                # "# HIGHER SANSKRIT GRAMMAR"
                # "## Chapter I. THE ALPHABET"
                # "# APPENDIX"
                if re.match(r'^#\s+HIGHER SANSKRIT GRAMMAR', line):
                    continue
                if re.match(r'^##\s+Chapter\s+[IVXLC]+\.', line):
                    continue
                if re.match(r'^#\s+APPENDIX', line):
                    continue
                # Skip standalone chapter titles
                if re.match(r'^#\s+[A-Z\s]+$', line) and len(line.strip()) < 50:
                    continue

            # Once we're inside a rule, keep everything
            if inside_rule or line.strip():
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines).strip()

    def extract_rule(self, rule_num: str, page_files: list, is_appendix: bool = False):
        """Extract a single rule from one or more pages."""

        debug = rule_num in ["325-328", "702-705", "961-963"]
        if debug:
            print(f"    [extract_rule] rule_num={rule_num}, num_pages={len(page_files)}")

        # Combine content from all pages for this rule
        combined_metadata = {}
        combined_content = []

        for page_file in sorted(page_files):
            content = page_file.read_text()

            # Split YAML and content
            yaml_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
            if not yaml_match:
                continue

            try:
                metadata = yaml.safe_load(yaml_match.group(1))
                body = yaml_match.group(2).strip()
            except:
                continue

            if debug:
                print(f"    [extract_rule] page={page_file.name}, body_before_clean={len(body)}")

            # Clean the body content (remove structural headers)
            body = self.clean_rule_content(body)

            if debug:
                print(f"    [extract_rule] page={page_file.name}, body_after_clean={len(body)}")
                if len(body) == 0:
                    print(f"    [extract_rule] WARNING: clean_rule_content removed all content!")
                    print(f"    [extract_rule] First 200 chars before clean: {yaml_match.group(2).strip()[:200]}")

            # Merge metadata (first page wins for most fields)
            if not combined_metadata:
                combined_metadata = metadata.copy()
            else:
                # Merge lists (handle both lists and non-list values)
                for key in ['topics', 'word_index', 'panini_refs', 'cross_refs']:
                    if key in metadata:
                        existing = combined_metadata.get(key, [])
                        new_value = metadata[key]

                        # Ensure both are lists
                        if not isinstance(existing, list):
                            existing = [existing] if existing else []
                        if not isinstance(new_value, list):
                            new_value = [new_value] if new_value else []

                        # Merge and deduplicate (only for hashable items)
                        merged = existing + new_value
                        try:
                            combined_metadata[key] = list(set(merged))
                        except TypeError:
                            # If items aren't hashable (e.g., dicts), just append
                            combined_metadata[key] = merged

            combined_content.append(body)

        # Create rule file in appropriate directory
        output_dir = self.appendices_output if is_appendix else self.rules_output
        prefix = "appendix" if is_appendix else "rule"
        rule_file = output_dir / f"{prefix}_{rule_num.replace('-', '_')}.md"

        # Build new YAML metadata
        new_metadata = {
            'rule': f'§ {rule_num}',
            'source_pages': [int(f.stem.split('_')[1]) for f in page_files],
        }

        # Copy relevant fields
        for key in ['chapter', 'section', 'topics', 'word_index', 'panini_refs', 'cross_refs']:
            if key in combined_metadata:
                new_metadata[key] = combined_metadata[key]

        # Write rule file
        final_content = '\n\n'.join(combined_content)
        if debug:
            print(f"    [extract_rule] final combined_content length={len(final_content)}")

        with open(rule_file, 'w', encoding='utf-8') as f:
            f.write('---\n')
            f.write(yaml.dump(new_metadata, allow_unicode=True, sort_keys=False))
            f.write('---\n\n')
            f.write(final_content)

        return rule_file

    def expand_rule_range(self, rule_num: str):
        """Expand rule range like '16-19' into individual numbers [16, 17, 18, 19]."""
        if '-' in rule_num and re.match(r'^\d+-\d+$', rule_num):
            start, end = map(int, rule_num.split('-'))
            return list(range(start, end + 1))
        elif rule_num.isdigit():
            return [int(rule_num)]
        else:
            return []

    def split_rule_content(self, content: str, rule_num: int, is_first_in_range: bool = False):
        """Extract content for a specific rule number from combined content.

        Looks for ## § N headers and extracts everything until the next ## § header.
        If the rule has no header and it's the first in range, returns content before first header.
        """
        # Debug for specific problematic rules
        debug = rule_num in [326, 327, 702, 962]
        if debug:
            print(f"    [split_rule_content] rule={rule_num}, is_first_in_range={is_first_in_range}")
            print(f"    [split_rule_content] content length={len(content)}")

        lines = content.split('\n')
        result_lines = []
        inside_target_rule = False
        found_any_header = False
        current_range_start = None
        current_range_end = None
        found_exact_match = False

        for line in lines:
            # Check if this is a rule header - handles "## § 123", "## § 123.", or "## § 77-78"
            rule_match = re.match(r'^##\s*§\s*(\d+)(?:-(\d+))?\.?', line)
            if rule_match:
                found_any_header = True
                found_num = int(rule_match.group(1))
                # Check if we have a range like "§ 77-78"
                end_num = int(rule_match.group(2)) if rule_match.group(2) else found_num

                # Check if this header is for our target rule
                is_exact_match = (found_num == rule_num and rule_match.group(2) is None)
                is_range_match = (found_num <= rule_num <= end_num)

                if is_exact_match:
                    # Exact match found - prefer this over any range match
                    if inside_target_rule and not found_exact_match:
                        # We were in a range match, now found exact - reset and use exact
                        result_lines = []
                    inside_target_rule = True
                    found_exact_match = True
                    current_range_start = found_num
                    current_range_end = end_num
                elif is_range_match:
                    # This range includes our target rule
                    if not found_exact_match:  # Only use range match if we haven't found exact
                        if not inside_target_rule:
                            inside_target_rule = True
                        current_range_start = found_num
                        current_range_end = end_num
                else:
                    # This header is not our target
                    if found_exact_match:
                        # We found exact match earlier, stop here
                        break
                    elif inside_target_rule:
                        # We're in a range match - check if this header is outside the range
                        if current_range_start and current_range_end:
                            if found_num > current_range_end:
                                # Header is outside our range, stop
                                break
                            # Otherwise, this header is within range (e.g., § 326 within § 325-328), continue
                        else:
                            # Not our target and no range tracking, stop
                            break
                    elif is_first_in_range:
                        # We hit a header for a different rule and haven't found ours
                        break

            # Collect lines when inside target rule
            if inside_target_rule:
                result_lines.append(line)
            elif is_first_in_range and not found_any_header:
                # Collect content before first header for first rule
                result_lines.append(line)

        result = '\n'.join(result_lines).strip()
        if debug:
            print(f"    [split_rule_content] result length={len(result)}, found_exact_match={found_exact_match}")
            print(f"    [split_rule_content] inside_target_rule={inside_target_rule}, found_any_header={found_any_header}")
        return result

    def extract_all_rules(self):
        """Extract all rules into individual files."""
        print("\n🔨 Extracting main grammar rules...")

        main_count = 0
        appendix_count = 0
        expanded_count = 0

        # Sort rules numerically
        def sort_key(rule_str):
            # Extract first number from "123" or "123-125"
            match = re.match(r'(\d+)', rule_str)
            return int(match.group(1)) if match else 0

        # Extract main grammar rules
        for rule_num in sorted(self.rule_to_pages.keys(), key=sort_key):
            page_files = self.rule_to_pages[rule_num]

            try:
                # Check if this is a range
                expanded = self.expand_rule_range(rule_num)

                # Debug specific ranges
                if rule_num in ["325-328", "702-705", "961-963"]:
                    print(f"  [extract_all_rules] Processing rule_num={rule_num}, expanded={expanded}")

                if len(expanded) > 1:
                    # This is a range - create individual files only, no combined file
                    # First create a temporary combined file to extract content from
                    if rule_num in ["325-328", "702-705", "961-963"]:
                        print(f"    [extract_all_rules] Calling extract_rule for {rule_num}")
                    temp_combined = self.extract_rule(rule_num, page_files, is_appendix=False)
                    if rule_num in ["325-328", "702-705", "961-963"]:
                        print(f"    [extract_all_rules] extract_rule returned: {temp_combined}")
                    combined_content = temp_combined.read_text()

                    # Extract just the body content (after YAML front matter)
                    body_match = re.match(r'^---\n.*?\n---\n\n(.*)$', combined_content, re.DOTALL)
                    if body_match:
                        full_body = body_match.group(1)

                        # Split into individual rule contents
                        extracted_any = False
                        for idx, individual_num in enumerate(expanded):
                            individual_file = self.rules_output / f"rule_{individual_num}.md"
                            if not individual_file.exists():
                                # Extract just this rule's content
                                # is_first_in_range should be True if this is the first rule we're extracting from this range
                                is_first = (idx == 0) or not extracted_any

                                # Debug for specific problematic rules
                                if individual_num in [326, 327, 702, 962]:
                                    print(f"  DEBUG: Extracting rule {individual_num} from range {rule_num}")
                                    print(f"         is_first={is_first}, idx={idx}, extracted_any={extracted_any}")
                                    print(f"         full_body length: {len(full_body)} chars")
                                    print(f"         First 100 chars: {full_body[:100]}")

                                rule_content = self.split_rule_content(full_body, individual_num, is_first_in_range=is_first)

                                if rule_content:
                                    with open(individual_file, 'w', encoding='utf-8') as f:
                                        f.write(f'---\n')
                                        f.write(f'rule: § {individual_num}\n')
                                        f.write(f'source_pages: {[int(p.stem.split("_")[1]) for p in page_files]}\n')
                                        f.write(f'---\n\n')
                                        f.write(rule_content)
                                    expanded_count += 1
                                    main_count += 1
                                    extracted_any = True
                                else:
                                    if individual_num in [326, 327, 702, 962]:
                                        print(f"  DEBUG: split_rule_content returned empty/None")
                                    print(f"  ⚠️  Rule {individual_num} (from range {rule_num}): empty content, skipping")

                    # Delete the temporary combined file
                    temp_combined.unlink()
                else:
                    # Single rule - create file normally
                    self.extract_rule(rule_num, page_files, is_appendix=False)
                    main_count += 1

                if main_count % 50 == 0:
                    print(f"   Extracted {main_count} main rules...")
            except Exception as e:
                print(f"   ❌ Failed to extract rule {rule_num}: {e}")

        # Extract appendix rules
        if self.appendix_to_pages:
            print("\n🔨 Extracting appendix sections...")
            for rule_num in sorted(self.appendix_to_pages.keys(), key=sort_key):
                page_files = self.appendix_to_pages[rule_num]

                try:
                    # Check if this is a range
                    expanded = self.expand_rule_range(rule_num)

                    if len(expanded) > 1:
                        # This is a range - create individual files only, no combined file
                        temp_combined = self.extract_rule(rule_num, page_files, is_appendix=True)
                        combined_content = temp_combined.read_text()

                        # Extract just the body content (after YAML front matter)
                        body_match = re.match(r'^---\n.*?\n---\n\n(.*)$', combined_content, re.DOTALL)
                        if body_match:
                            full_body = body_match.group(1)

                            for idx, individual_num in enumerate(expanded):
                                individual_file = self.appendices_output / f"appendix_{individual_num}.md"
                                if not individual_file.exists():
                                    # Extract just this rule's content
                                    is_first = (idx == 0)
                                    rule_content = self.split_rule_content(full_body, individual_num, is_first_in_range=is_first)

                                    if rule_content:
                                        with open(individual_file, 'w', encoding='utf-8') as f:
                                            f.write(f'---\n')
                                            f.write(f'rule: § {individual_num}\n')
                                            f.write(f'appendix: true\n')
                                            f.write(f'source_pages: {[int(p.stem.split("_")[1]) for p in page_files]}\n')
                                            f.write(f'---\n\n')
                                            f.write(rule_content)
                                        appendix_count += 1

                        # Delete the temporary combined file
                        temp_combined.unlink()
                    else:
                        # Single appendix section - create file normally
                        self.extract_rule(rule_num, page_files, is_appendix=True)
                        appendix_count += 1

                except Exception as e:
                    print(f"   ❌ Failed to extract appendix {rule_num}: {e}")

        print(f"\n✅ Extracted {main_count} rules to {self.rules_output}/")
        if expanded_count:
            print(f"✅ Created {expanded_count} individual rule files from ranges")
        if appendix_count:
            print(f"✅ Extracted {appendix_count} appendix sections to {self.appendices_output}/")
        return main_count + appendix_count + expanded_count

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Extract individual rules from structured pages')
    parser.add_argument('--repo', default='/Users/skmnktl/Downloads/ocr', help='Repository path')
    args = parser.parse_args()

    extractor = RuleExtractor(args.repo)
    extractor.scan_pages()
    extractor.extract_all_rules()

if __name__ == "__main__":
    main()
