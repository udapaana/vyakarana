#!/usr/bin/env python3
"""
Refined analysis with better filtering of OCR errors
"""

import re
import json
from pathlib import Path
from collections import defaultdict

raw_dir = Path("raw_pages")
pages = sorted(raw_dir.glob("page_*.txt"))

print(f"📚 Analyzing {len(pages)} raw OCR pages...\n")

# Data structures
chapters = []
rules = defaultdict(list)

# Better patterns
chapter_pattern = re.compile(r'(^|\n)\s*CHAPTER\s+([IVX]+)|Chapter\s+([IVX]+)', re.MULTILINE | re.IGNORECASE)
# Only match § followed by 1-3 digit numbers (filter out OCR errors like 444449)
rule_pattern = re.compile(r'§\s*(\d{1,3})[\.\s,]')

print("🔍 Scanning all pages...\n")

for page_file in pages:
    page_num = int(re.search(r'page_(\d+)', page_file.name).group(1))
    
    with open(page_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Find chapters
    for match in chapter_pattern.finditer(content):
        chapter_num = match.group(2) or match.group(3)
        if chapter_num:
            chapters.append({
                'number': chapter_num,
                'page': page_num,
                'line': content[:match.start()].count('\n') + 1
            })
    
    # Find rules (1-3 digits only to avoid OCR errors)
    for match in rule_pattern.finditer(content):
        rule_num = int(match.group(1))
        if 1 <= rule_num <= 999:  # Sanity check
            rules[rule_num].append(page_num)

print(f"📊 Found {len(chapters)} chapter markers")
print(f"📊 Found rule numbers: {len(rules)} unique rules")

all_rules = sorted(rules.keys())
if all_rules:
    print(f"📈 Rule range: §{all_rules[0]} to §{all_rules[-1]}\n")

# Compare with v7
print("🔍 Loading v7 to compare...\n")
v7_file = Path("output/kales_sanskrit_grammar_v7.md")
with open(v7_file, 'r') as f:
    v7_content = f.read()

v7_rules = set()
for match in re.finditer(r'####\s*§\s*(\d+)\.', v7_content):
    v7_rules.add(int(match.group(1)))

print(f"📄 V7 contains: {len(v7_rules)} unique rules")
print(f"📄 Raw pages contain: {len(rules)} unique rules\n")

# Rules in raw but not in v7
missing_from_v7 = set(rules.keys()) - v7_rules
# Rules in v7 but not in raw  
extra_in_v7 = v7_rules - set(rules.keys())

if missing_from_v7:
    print(f"❌ Rules in raw pages but MISSING from v7 ({len(missing_from_v7)}):\n")
    missing_sorted = sorted(missing_from_v7)
    
    # Group into ranges
    ranges = []
    start = missing_sorted[0]
    end = missing_sorted[0]
    
    for i in range(1, len(missing_sorted)):
        if missing_sorted[i] == end + 1:
            end = missing_sorted[i]
        else:
            if start == end:
                ranges.append(f"§{start}")
            else:
                ranges.append(f"§{start}-§{end}")
            start = missing_sorted[i]
            end = missing_sorted[i]
    
    if start == end:
        ranges.append(f"§{start}")
    else:
        ranges.append(f"§{start}-§{end}")
    
    for r in ranges:
        print(f"  {r}")
else:
    print("✅ All rules from raw pages are in v7!\n")

if extra_in_v7:
    print(f"\n⚠️  Rules in v7 but NOT in raw ({len(extra_in_v7)}):")
    for r in sorted(extra_in_v7)[:20]:
        print(f"  §{r}")

# Save detailed mapping
print(f"\n💾 Saving rule-to-page mapping...")
output = {
    'total_raw_pages': len(pages),
    'chapters': chapters,
    'raw_rules_count': len(rules),
    'v7_rules_count': len(v7_rules),
    'missing_from_v7': sorted(missing_from_v7),
    'rules_to_pages': {k: v for k, v in sorted(rules.items())}
}

with open('raw_vs_v7_analysis.json', 'w') as f:
    json.dump(output, f, indent=2)

print("✅ Complete!\n")
