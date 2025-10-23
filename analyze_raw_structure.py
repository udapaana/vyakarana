#!/usr/bin/env python3
"""
Comprehensive analysis of raw OCR pages to identify:
1. All chapters and their page ranges
2. All section headers and their page locations
3. All rule numbers and their page locations
4. Missing sections and incomplete sections
"""

import re
from pathlib import Path
from collections import defaultdict

raw_dir = Path("raw_pages")
pages = sorted(raw_dir.glob("page_*.txt"))

print(f"📚 Analyzing {len(pages)} raw OCR pages...\n")

# Data structures
chapters = []
sections = []
rules = []

# Patterns to match
chapter_pattern = re.compile(r'CHAPTER\s+([IVX]+)|Chapter\s+([IVX]+)', re.IGNORECASE)
section_pattern = re.compile(r'(^|\n)(I{1,3}|IV|VI{0,3}|IX|X{1,3})\.\s+[A-Z][A-Z\s]+', re.MULTILINE)
rule_pattern = re.compile(r'§\s*(\d+)[.\s]')

print("🔍 Scanning all pages...\n")

for page_file in pages:
    page_num = int(re.search(r'page_(\d+)', page_file.name).group(1))
    
    with open(page_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Find chapters
    for match in chapter_pattern.finditer(content):
        chapter_num = match.group(1) or match.group(2)
        chapters.append({
            'number': chapter_num,
            'page': page_num,
            'text': match.group(0)
        })
    
    # Find rules
    for match in rule_pattern.finditer(content):
        rule_num = int(match.group(1))
        rules.append({
            'number': rule_num,
            'page': page_num,
            'context': content[max(0, match.start()-50):match.end()+50]
        })

# Group rules by number
rules_by_num = defaultdict(list)
for rule in rules:
    rules_by_num[rule['number']].append(rule['page'])

print(f"📊 Found {len(chapters)} chapter markers across pages")
print(f"📊 Found {len(rules)} rule markers (§) across pages")
print(f"📊 Unique rule numbers: {len(rules_by_num)}\n")

# Identify all unique rule numbers
all_rule_nums = sorted(rules_by_num.keys())

print(f"📈 Rule number range: §{all_rule_nums[0]} to §{all_rule_nums[-1]}\n")

# Find gaps in raw pages
print("🔍 Analyzing gaps in raw OCR pages:\n")
gaps_in_raw = []
for i in range(len(all_rule_nums) - 1):
    current = all_rule_nums[i]
    next_num = all_rule_nums[i + 1]
    if next_num - current > 1:
        missing = list(range(current + 1, next_num))
        gaps_in_raw.extend(missing)

if gaps_in_raw:
    print(f"  Found {len(gaps_in_raw)} gaps in raw OCR pages:")
    # Group consecutive gaps
    gap_ranges = []
    start = gaps_in_raw[0]
    end = gaps_in_raw[0]
    
    for i in range(1, len(gaps_in_raw)):
        if gaps_in_raw[i] == end + 1:
            end = gaps_in_raw[i]
        else:
            if start == end:
                gap_ranges.append(f"§{start}")
            else:
                gap_ranges.append(f"§{start}-§{end}")
            start = gaps_in_raw[i]
            end = gaps_in_raw[i]
    
    if start == end:
        gap_ranges.append(f"§{start}")
    else:
        gap_ranges.append(f"§{start}-§{end}")
    
    for r in gap_ranges[:20]:
        print(f"    {r}")
    if len(gap_ranges) > 20:
        print(f"    ... and {len(gap_ranges) - 20} more")
else:
    print("  ✅ No gaps in raw OCR! All consecutive rule numbers present.")

print(f"\n💾 Saving detailed analysis to raw_pages_analysis.json...")

import json
output = {
    'total_pages': len(pages),
    'chapters_found': len(chapters),
    'total_rule_markers': len(rules),
    'unique_rules': len(rules_by_num),
    'rule_range': [all_rule_nums[0], all_rule_nums[-1]],
    'gaps_in_raw': gaps_in_raw,
    'all_rules': all_rule_nums,
    'rules_by_page': {k: v for k, v in rules_by_num.items()},
    'chapters': chapters
}

with open('raw_pages_analysis.json', 'w') as f:
    json.dump(output, f, indent=2)

print("✅ Analysis complete!\n")
