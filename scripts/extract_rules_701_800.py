#!/usr/bin/env python3
"""
Comprehensive extraction script for Sanskrit Grammar rules 701-800
Reads OCR files and generates properly formatted markdown files
"""

import os
import re
import glob
from pathlib import Path

# Base paths
BASE_DIR = Path("/Users/skmnktl/Downloads/ocr")
OCR_DIR = BASE_DIR / "phase1_ocr/sources/official_1931"
RULES_DIR = BASE_DIR / "phase3_rules"

def read_ocr_file(page_num):
    """Read OCR content from a specific page"""
    filepath = OCR_DIR / f"{page_num}.txt"
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def find_rule_content(rule_num, start_page=441, end_page=490):
    """Find the OCR content for a specific rule across pages"""
    for page in range(start_page, end_page):
        content = read_ocr_file(page)
        # Look for the rule header
        pattern = rf"§ {rule_num}\..*"
        if re.search(pattern, content):
            return page, content
    return None, None

def extract_all_rules():
    """Extract all rules from OCR files"""
    # Read all relevant OCR files
    all_ocr = {}
    for page in range(441, 490):
        content = read_ocr_file(page)
        if content:
            all_ocr[page] = content

    # Find all rule occurrences
    rule_locations = {}
    for page, content in all_ocr.items():
        matches = re.finditer(r'§ (\d+)\.', content)
        for match in matches:
            rule_num = int(match.group(1))
            if 701 <= rule_num <= 800:
                if rule_num not in rule_locations:
                    rule_locations[rule_num] = []
                rule_locations[rule_num].append(page)

    return rule_locations, all_ocr

def main():
    """Main extraction process"""
    print("Extracting rules 701-800...")
    print("=" * 60)

    rule_locations, all_ocr = extract_all_rules()

    print(f"Found {len(rule_locations)} rules in OCR files")
    print("\nRule locations:")
    for rule_num in sorted(rule_locations.keys()):
        pages = rule_locations[rule_num]
        print(f"  § {rule_num}: pages {', '.join(map(str, pages))}")

    # Count existing extractions
    extracted_count = 0
    stub_count = 0

    for i in range(701, 801):
        filepath = RULES_DIR / f"rule_{i}.md"
        if filepath.exists():
            with open(filepath, 'r') as f:
                content = f.read()
                if 'chapter: TBD' in content or '[Rule Title - To Be Enhanced]' in content:
                    stub_count += 1
                else:
                    extracted_count += 1

    print(f"\nCurrent status:")
    print(f"  Extracted: {extracted_count}")
    print(f"  Stubs: {stub_count}")
    print(f"  Total files: {extracted_count + stub_count}")

    return rule_locations

if __name__ == "__main__":
    main()
