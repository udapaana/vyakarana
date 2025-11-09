#!/usr/bin/env python3
"""
Batch extract rules 211-300 from OCR sources.
This script automates the extraction while maintaining the RULE_EXTRACTION_SCHEMA.md standard.
"""

import re
import os
from pathlib import Path

# Base paths
OCR_DIR = Path("/Users/skmnktl/Downloads/ocr/phase1_ocr/sources/official_1931")
OUTPUT_DIR = Path("/Users/skmnktl/Downloads/ocr/phase3_rules")

# Rule range to process
START_RULE = 211
END_RULE = 300

def find_rule_in_ocr(rule_num):
    """Find which OCR file contains a specific rule."""
    pattern = f"§ {rule_num}"
    for ocr_file in sorted(OCR_DIR.glob("*.txt")):
        try:
            content = ocr_file.read_text(encoding='utf-8')
            if pattern in content:
                return ocr_file
        except:
            continue
    return None

def extract_rule_content(rule_num, ocr_file):
    """Extract content for a specific rule from OCR file."""
    content = ocr_file.read_text(encoding='utf-8')

    # Find the rule start
    rule_pattern = rf"§ {rule_num}\.?\s+"
    match = re.search(rule_pattern, content)
    if not match:
        return None

    start_pos = match.start()

    # Find the next rule (end boundary)
    next_rule_pattern = rf"§ {rule_num + 1}\.?\s+"
    next_match = re.search(next_rule_pattern, content[start_pos:])

    if next_match:
        end_pos = start_pos + next_match.start()
        rule_text = content[start_pos:end_pos]
    else:
        # If no next rule, take until end of section or page
        rule_text = content[start_pos:]

    return rule_text.strip()

def parse_rule_title(rule_text):
    """Extract rule title from OCR content."""
    # Try to find title after rule number
    title_match = re.search(r'§ \d+\.?\s+(.+?)(?:\n|$)', rule_text)
    if title_match:
        title = title_match.group(1).strip()
        # Clean up common OCR artifacts
        title = re.sub(r'\s+', ' ', title)
        return title
    return "TBD"

def extract_panini_refs(rule_text):
    """Extract Pāṇini references from footnotes."""
    refs = []
    # Look for patterns like "Pān. II. 2. 9"
    panini_pattern = r'Pān\.\s+([IVX]+)\.\s*(\d+)\.\s*(\d+)'
    matches = re.findall(panini_pattern, rule_text)
    for match in matches:
        refs.append(f"{match[0]}.{match[1]}.{match[2]}")
    return refs

def main():
    print(f"Extracting rules {START_RULE}-{END_RULE}...")

    extracted_count = 0
    failed_rules = []

    for rule_num in range(START_RULE, END_RULE + 1):
        print(f"Processing rule {rule_num}...", end=" ")

        # Find OCR file
        ocr_file = find_rule_in_ocr(rule_num)
        if not ocr_file:
            print(f"NOT FOUND in OCR")
            failed_rules.append(rule_num)
            continue

        # Extract content
        rule_content = extract_rule_content(rule_num, ocr_file)
        if not rule_content:
            print(f"EXTRACTION FAILED")
            failed_rules.append(rule_num)
            continue

        # Parse metadata
        title = parse_rule_title(rule_content)
        panini_refs = extract_panini_refs(rule_content)

        # Generate markdown file
        output_file = OUTPUT_DIR / f"rule_{rule_num}.md"

        # Basic template - will need manual review
        markdown = f"""---
rule_number: {rule_num}
rule_id: "§ {rule_num}"
title: "{title}"
chapter: "Compounds"
section: "tatpurusha-compounds"
page_start: {ocr_file.stem}
page_end: {ocr_file.stem}
topics:
  - compounds
word_index: []
panini_refs: {panini_refs if panini_refs else []}
cross_refs:
  - "§ {rule_num - 1}"
  - "§ {rule_num + 1}"
examples_count: 0
has_table: false
has_footnotes: {'true' if 'Pān.' in rule_content or 'Vārt' in rule_content else 'false'}
source_pages:
  - "{ocr_file.name}"
---

## § {rule_num}. {title}

<!-- NEEDS MANUAL FORMATTING -->
<!-- Original OCR content below - convert to proper markdown with Sanskrit tagging -->

{rule_content[:500]}...

<!-- TODO:
1. Format Sanskrit terms with @deva[] @[IAST]
2. Extract and format footnotes
3. Add proper examples
4. Update metadata
-->
"""

        # Don't overwrite if already properly extracted
        if output_file.exists():
            existing = output_file.read_text()
            if 'chapter: "Compounds"' in existing and 'NEEDS MANUAL FORMATTING' not in existing:
                print(f"SKIP (already extracted)")
                extracted_count += 1
                continue

        output_file.write_text(markdown, encoding='utf-8')
        print(f"OK")
        extracted_count += 1

    print(f"\n=== Summary ===")
    print(f"Extracted: {extracted_count}/{END_RULE - START_RULE + 1}")
    if failed_rules:
        print(f"Failed rules: {failed_rules}")

if __name__ == "__main__":
    main()
