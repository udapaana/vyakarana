#!/usr/bin/env python3
"""
Analyze stub files to identify which rules need enhancement
and group them by page ranges for batch processing.
"""

import re
import yaml
from pathlib import Path
from collections import defaultdict

# Find all stub files
stub_rules = []
enhanced_rules = []

for rule_file in sorted(Path('phase3_rules').glob('rule_*.md')):
    with open(rule_file, encoding='utf-8') as f:
        content = f.read()

    # Check if it's a stub
    if '[Rule Title - To Be Enhanced]' in content or 'TBD' in content[:500]:
        # Extract rule number and page
        yaml_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if yaml_match:
            try:
                metadata = yaml.safe_load(yaml_match.group(1))
                rule_num = int(re.sub(r'[^\d]', '', str(metadata.get('rule', ''))))
                page = metadata.get('page', 'unknown')
                stub_rules.append((rule_num, page, rule_file.name))
            except:
                pass
    else:
        # Fully enhanced
        yaml_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if yaml_match:
            try:
                metadata = yaml.safe_load(yaml_match.group(1))
                rule_num = int(re.sub(r'[^\d]', '', str(metadata.get('rule', ''))))
                enhanced_rules.append(rule_num)
            except:
                pass

print(f"Analysis of phase3_rules/")
print(f"=" * 60)
print(f"Fully enhanced: {len(enhanced_rules)} rules")
print(f"Stubs to enhance: {len(stub_rules)} rules")
print(f"Total: {len(enhanced_rules) + len(stub_rules)} rules")
print(f"=" * 60)

# Group stubs by page ranges
page_groups = defaultdict(list)
for rule_num, page, filename in stub_rules:
    # Try to parse page number
    try:
        page_str = str(page)
        page_int = int(re.sub(r'[^\d]', '', page_str)) if page_str != 'unknown' else 0

        # Group into ranges of ~20 pages
        if page_int > 0:
            range_start = (page_int // 20) * 20
            page_groups[range_start].append((rule_num, page, filename))
    except:
        page_groups['unknown'].append((rule_num, page, filename))

print(f"\nStubs grouped by page ranges:")
print(f"-" * 60)
for range_start in sorted([k for k in page_groups.keys() if k != 'unknown']):
    rules = page_groups[range_start]
    pages = sorted(set(str(r[1]) for r in rules))
    range_end = range_start + 19
    print(f"Pages {range_start:3d}-{range_end:3d}: {len(rules):3d} rules (rules {min(r[0] for r in rules):3d}-{max(r[0] for r in rules):3d})")

if 'unknown' in page_groups:
    print(f"Unknown pages: {len(page_groups['unknown'])} rules")

# Show first few ranges in detail
print(f"\n{'=' * 60}")
print(f"First 3 page ranges (detailed):")
print(f"=" * 60)
for i, range_start in enumerate(sorted([k for k in page_groups.keys() if k != 'unknown'])[:3]):
    rules = page_groups[range_start]
    range_end = range_start + 19
    print(f"\nRange {i+1}: Pages {range_start}-{range_end}")
    print(f"  Rules to enhance: {', '.join(f'§{r[0]}' for r in sorted(rules[:10]))}", end='')
    if len(rules) > 10:
        print(f" ... ({len(rules)} total)")
    else:
        print()

    # Get unique pages in this range
    pages = sorted(set(str(r[1]) for r in rules))
    print(f"  Pages needed: {', '.join(str(p) for p in pages[:15])}", end='')
    if len(pages) > 15:
        print(f" ... ({len(pages)} total)")
    else:
        print()

print(f"\n{'=' * 60}")
print(f"Next steps:")
print(f"1. Process stubs in batches by page range")
print(f"2. Create window input files for each range")
print(f"3. Feed to Claude for enhancement")
print("=" * 60)
