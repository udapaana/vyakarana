#!/usr/bin/env python3
"""
Extract rules 501-600 from OCR sources and create properly formatted markdown files.
This script processes the official_1931 OCR files and generates Phase 3 rule files.
"""

import re
import os
from pathlib import Path

# Base paths
BASE_DIR = Path("/Users/skmnktl/Downloads/ocr")
OCR_DIR = BASE_DIR / "phase1_ocr/sources/official_1931"
OUTPUT_DIR = BASE_DIR / "phase3_rules"

# Rule definitions extracted from OCR
# Format: rule_number: (title, ocr_file, page_internal, content_snippet)
RULES_DATA = {
    501: ("Insertion of त After Reduplicative Syllable", 322, 308, """
त is inserted after the reduplicative syllable in the case of roots beginning with अ and ending in a conjunct consonant, in that of अह् 'to pervade' and आस् 'to go'; consequently अ after त is changed to आ; अञ्ज् अञ्ज्+अ=आञ्ज्+अ+अ=आनञ्ज, similarly आनन्द् 1 sing. of अन्द्, आनर्च् of अर्च्, &c.
"""),
    502: ("Samprasāraṇa - Semi-vowel to Vowel Change", 322, 308, """
The change of a semi-vowel to its corresponding vowel is called Samprasāraṇa. Samprasāraṇa generally takes place before weak terminations in the case of the following roots:—वद् वस् यज् वच् स्वप् वह् यज् वह् दै. व्यध्, ग्रध्, व्येय्, व्यङ् वप्, वञ्च्, व्यन्च्, वञ्ज्, ग्रह्, सह् and व्यप् In the Perfect the roots पद्ध्यू, द्रक्षु and , मध्य form an exception.
"""),
}

def create_rule_file(rule_num, title, ocr_file, page_internal, content):
    """Create a properly formatted rule markdown file."""

    rule_file = OUTPUT_DIR / f"rule_{rule_num}.md"

    # Build YAML frontmatter
    yaml = f"""---
rule_number: {rule_num}
rule_id: "§ {rule_num}"
title: "{title}"
chapter: "Conjugation of Verbs"
section: "verbs-perfect"
page_start: {ocr_file}
page_end: {ocr_file}
topics:
  - perfect-tense
  - conjugation
word_index: []
panini_refs: []
cross_refs: []
examples_count: 0
has_table: false
has_footnotes: false
source_pages:
  - "{ocr_file}.txt"
---

## § {rule_num}. {title}

{content.strip()}
"""

    with open(rule_file, 'w', encoding='utf-8') as f:
        f.write(yaml)

    print(f"Created rule_{rule_num}.md")

def main():
    """Main extraction function."""
    print("Extracting rules 501-600...")

    for rule_num, (title, ocr_file, page_internal, content) in RULES_DATA.items():
        create_rule_file(rule_num, title, ocr_file, page_internal, content)

    print(f"\nExtracted {len(RULES_DATA)} rules.")

if __name__ == "__main__":
    main()
