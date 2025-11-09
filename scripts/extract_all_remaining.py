#!/usr/bin/env python3
"""
Comprehensive extraction script for all remaining Sanskrit Grammar rules.
Reads OCR, extracts rules, applies proper formatting per RULE_EXTRACTION_SCHEMA.md
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# OCR source directory
OCR_DIR = Path("phase1_ocr/sources/official_1931")
RULES_DIR = Path("phase3_rules")

# Chapter mappings based on page ranges
CHAPTER_MAP = {
    (1, 25): ("The Alphabet", "alphabet"),
    (26, 37): ("Rules of Sandhi", "sandhi"),
    (38, 77): ("Subanta or Declension", "declension"),
    (78, 139): ("Subanta or Declension", "declension"),
    (140, 193): ("Kṛt - Primary Nominal Bases", "compounds"),
    (194, 267): ("Taddhita - Secondary Nominal Bases", "compounds"),
    (268, 330): ("Conjugation of Verbs", "verbs"),
    (331, 453): ("Conjugation of Verbs", "verbs"),
    (454, 488): ("Primary Nominal Bases", "participles"),
    (489, 525): ("Syntax", "syntax"),
    (526, 548): ("Syntax", "syntax"),
}

def get_chapter_for_page(page: int) -> Tuple[str, str]:
    """Get chapter and section for a given page number"""
    for (start, end), (chapter, section) in CHAPTER_MAP.items():
        if start <= page <= end:
            return chapter, section
    return "TBD", "TBD"

def read_ocr_file(page_num: int) -> Optional[str]:
    """Read OCR content from a specific page file"""
    ocr_file = OCR_DIR / f"{page_num:03d}.txt"
    if not ocr_file.exists():
        return None
    return ocr_file.read_text(encoding='utf-8')

def find_rule_in_ocr(rule_num: int, start_page: int = 1, end_page: int = 732) -> Tuple[Optional[str], int]:
    """
    Find a specific rule in OCR files.
    Returns (content, page_number) or (None, 0) if not found
    """
    # Search pattern for rule marker
    patterns = [
        rf'§\s*{rule_num}\.?\s+',  # § 123. or § 123
        rf'§\s*{rule_num}\s*[A-Z]',  # § 123 TITLE
    ]

    for page in range(start_page, end_page + 1):
        content = read_ocr_file(page)
        if not content:
            continue

        for pattern in patterns:
            if re.search(pattern, content):
                return content, page

    return None, 0

def extract_rule_content(ocr_content: str, rule_num: int) -> str:
    """Extract the content for a specific rule from OCR"""
    # Find the start of this rule
    start_pattern = rf'§\s*{rule_num}\.?\s+'
    start_match = re.search(start_pattern, ocr_content)

    if not start_match:
        return ""

    start_pos = start_match.start()

    # Find the end (next rule or end of content)
    next_rule_pattern = rf'§\s*{rule_num + 1}\.?\s+'
    end_match = re.search(next_rule_pattern, ocr_content[start_pos + 50:])

    if end_match:
        end_pos = start_pos + 50 + end_match.start()
        rule_content = ocr_content[start_pos:end_pos]
    else:
        # Take reasonable chunk (next 500-1000 chars or until double newline)
        chunk = ocr_content[start_pos:start_pos + 1500]
        # Try to find natural break
        para_break = re.search(r'\n\n', chunk)
        if para_break and para_break.start() > 100:
            rule_content = chunk[:para_break.start()]
        else:
            rule_content = chunk[:800]

    return rule_content.strip()

def tag_sanskrit(text: str) -> str:
    """
    Add Sanskrit tags to Devanagari text.
    This is a simplified version - full implementation would use transliteration library
    """
    # Pattern: find Devanagari text
    dev_pattern = r'([ऀ-ॿ]+)'

    def replace_dev(match):
        dev_text = match.group(1)
        # Simplified IAST (would need proper transliteration)
        # For now, just tag the Devanagari
        return f'@deva[{dev_text}] @[IAST_placeholder]'

    return re.sub(dev_pattern, replace_dev, text)

def extract_title_from_content(content: str, rule_num: int) -> str:
    """Extract rule title from OCR content"""
    # Look for pattern: § N. Title or § N Title
    pattern = rf'§\s*{rule_num}\.?\s+([^\n]{{10,100}})'
    match = re.search(pattern, content)

    if match:
        title = match.group(1).strip()
        # Clean up common OCR artifacts
        title = re.sub(r'\s+', ' ', title)
        title = title.split('।')[0]  # Stop at Devanagari danda
        return title[:100]  # Limit length

    return f"Rule {rule_num}"

def create_rule_file(rule_num: int, force: bool = False) -> bool:
    """
    Extract and create a properly formatted rule file.
    Returns True if successful.
    """
    rule_file = RULES_DIR / f"rule_{rule_num:03d}.md"

    # Check if already complete
    if not force and rule_file.exists():
        content = rule_file.read_text()
        if '@deva[' in content and 'chapter: TBD' not in content:
            print(f"  §{rule_num}: Already complete, skipping")
            return True

    # Find rule in OCR
    print(f"  §{rule_num}: Searching OCR...", end='', flush=True)
    ocr_content, page = find_rule_in_ocr(rule_num)

    if not ocr_content:
        print(f" NOT FOUND in OCR")
        return False

    print(f" found on page {page}", end='', flush=True)

    # Extract content
    rule_content = extract_rule_content(ocr_content, rule_num)
    if not rule_content:
        print(f" - failed to extract content")
        return False

    # Get chapter info
    chapter, section = get_chapter_for_page(page)

    # Extract title
    title = extract_title_from_content(ocr_content, rule_num)

    # Create YAML frontmatter
    yaml = f"""---
rule: § {rule_num}
page: {page:03d}
source_pages:
  dli: [{page}]
  official_1931: [{page:03d}]
chapter: {chapter}
section: {section}
subsections: []
topics: []

hierarchy:
  chapter: {chapter}
  section: {section}

word_index: []
panini_refs: []
cross_refs: []

footnotes: []

confidence: medium

image: /images/page_{page:03d}.jpg
---

## § {rule_num}. {title}

{rule_content}

<!-- AUTO-EXTRACTED: Needs Sanskrit tagging review -->
"""

    # Write file
    rule_file.write_text(yaml, encoding='utf-8')
    print(f" - extracted!")
    return True

def main():
    """Main extraction process"""
    print("=" * 70)
    print("COMPREHENSIVE RULE EXTRACTION")
    print("=" * 70)

    # Get list of rules that need work
    rules_to_extract = []

    for num in range(39, 973):
        rule_file = RULES_DIR / f"rule_{num:03d}.md"

        if not rule_file.exists():
            rules_to_extract.append(num)
            continue

        content = rule_file.read_text()
        if 'chapter: TBD' in content or 'automated preliminary' in content:
            rules_to_extract.append(num)

    print(f"\nFound {len(rules_to_extract)} rules needing extraction\n")

    # Auto-confirm for batch processing
    if len(rules_to_extract) > 10:
        print(f"Auto-confirming extraction of {len(rules_to_extract)} rules...")

    # Extract rules
    success_count = 0
    fail_count = 0

    for i, rule_num in enumerate(rules_to_extract, 1):
        print(f"[{i}/{len(rules_to_extract)}]", end=' ')
        if create_rule_file(rule_num):
            success_count += 1
        else:
            fail_count += 1

    print("\n" + "=" * 70)
    print(f"EXTRACTION COMPLETE")
    print(f"  Success: {success_count}")
    print(f"  Failed:  {fail_count}")
    print("=" * 70)

if __name__ == "__main__":
    main()
