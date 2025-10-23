#!/usr/bin/env python3
import re
from pathlib import Path

# List of "missing" rule numbers from our gap analysis
missing_rules = [
    21, 22, 23, 27, 68, 69, 95, 96, 97, 102, 134, 249, 292, 333,
    342, 343, 349, 386, 387, 428, 429, 433, 450,
    488, 489, 490, 491, 492, 493, 543, 611, 612,
    631, 632, 633, 634, 635, 636, 637,
    706, 708, 711, 712,
    883, 884, 885, 886, 887, 888, 889,
    919, 920, 921, 922, 923, 962
]

# Search raw pages
raw_dir = Path("raw_pages")
found_in_raw = {}

print("🔍 Searching raw OCR pages for 'missing' rules...\n")

for rule_num in missing_rules:
    pattern = f"§ {rule_num}[^0-9]|§{rule_num}[^0-9]"
    for page_file in sorted(raw_dir.glob("page_*.txt")):
        with open(page_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if re.search(pattern, content):
                if rule_num not in found_in_raw:
                    found_in_raw[rule_num] = []
                found_in_raw[rule_num].append(page_file.name)

print(f"✅ Found in raw pages: {len(found_in_raw)} out of {len(missing_rules)} 'missing' rules\n")

if found_in_raw:
    print("Rules found in raw OCR but missing from v7:\n")
    for rule in sorted(found_in_raw.keys()):
        pages = ', '.join(found_in_raw[rule])
        print(f"  §{rule}: {pages}")

still_missing = set(missing_rules) - set(found_in_raw.keys())
if still_missing:
    print(f"\n❌ Still not found ({len(still_missing)}):")
    for rule in sorted(still_missing):
        print(f"  §{rule}")
