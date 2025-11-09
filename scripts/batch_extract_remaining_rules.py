#!/usr/bin/env python3
"""
Batch extract all remaining rules from Phase 1 OCR

This script processes OCR text and creates rule markdown files
for all rules not yet extracted.
"""

import re
import json
from pathlib import Path
from datetime import datetime

# Load existing status
status_file = Path('data/phase3_extraction_status.json')
status = json.load(open(status_file))
extracted = set(int(r.split('_')[1]) for r in status['extracted_rules'])

print(f"Already extracted: {len(extracted)} rules")
print(f"Target: 972 rules")
print(f"Remaining: {972 - len(extracted)} rules")

# Simplified rule template
def create_rule_stub(rule_num, page_num):
    """Create a minimal rule stub for batch processing"""
    # Convert page_num to int for formatting
    try:
        page_int = int(page_num)
    except:
        page_int = 0

    return f"""---
rule: § {rule_num}
page: {page_num}
source_pages:
  dli: [{page_num}]
  official_1931: []
chapter: TBD
section: TBD
subsections: []
topics: []

hierarchy:
  chapter: TBD
  section: TBD

word_index: []
panini_refs: []
cross_refs: []
confidence: medium

image: /images/page_{page_int:03d}.jpg
---

## § {rule_num}. [Rule Title - To Be Enhanced]

[Rule content to be extracted and formatted]

**Note:** This is a preliminary extraction stub. Requires enhancement with:
- Full rule content from multi-source OCR
- Proper Sanskrit tagging (@deva[] @[])
- Complete metadata
- Cross-references and Pāṇini sūtra citations
"""

# Find rules to extract
rules_to_extract = []
for page_file in sorted(Path('phase1_ocr/claude').glob('page_*.txt')):
    try:
        with open(page_file, encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Find rule numbers on this page
        rule_nums = re.findall(r'§\s*(\d+)', content)
        page_num = page_file.stem.replace('page_', '').replace('a', '').replace('b', '').replace('c', '')

        for rule_str in set(rule_nums):
            rule_num = int(rule_str)
            if 1 <= rule_num <= 972 and rule_num not in extracted:
                rules_to_extract.append((rule_num, page_num))
    except Exception as e:
        print(f"Error processing {page_file}: {e}")
        continue

rules_to_extract = sorted(set(rules_to_extract), key=lambda x: x[0])
print(f"\nFound {len(rules_to_extract)} rules to extract")

# Create stub files
output_dir = Path('phase3_rules')
output_dir.mkdir(exist_ok=True)

created_count = 0
for rule_num, page_num in rules_to_extract:
    output_file = output_dir / f'rule_{rule_num:03d}.md'

    if output_file.exists():
        continue

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(create_rule_stub(rule_num, page_num))

    created_count += 1
    if created_count % 50 == 0:
        print(f"  Created {created_count} stubs...")

print(f"\nCreated {created_count} new rule stub files")
print(f"\nNext step: Enhance stubs with full content using multi-source OCR")
