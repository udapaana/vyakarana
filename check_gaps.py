#!/usr/bin/env python3
import re
from pathlib import Path
from collections import defaultdict

# Find all rule files
v8_dir = Path("v8_sections")
all_files = sorted(v8_dir.rglob("s*.md"))

# Extract rule numbers from filenames
rules = []
for f in all_files:
    match = re.match(r's(\d+)\.md', f.name)
    if match:
        rules.append({
            'number': int(match.group(1)),
            'file': str(f.relative_to(v8_dir))
        })

# Sort by rule number
rules.sort(key=lambda x: x['number'])

print(f"📊 Total files found: {len(rules)}\n")
print(f"📝 Rule range: §{rules[0]['number']} to §{rules[-1]['number']}\n")

# Check for gaps
gaps = []
duplicates = defaultdict(list)

for i in range(len(rules)):
    num = rules[i]['number']
    duplicates[num].append(rules[i]['file'])
    
    if i > 0:
        prev_num = rules[i-1]['number']
        if num - prev_num > 1:
            # Found a gap
            missing = list(range(prev_num + 1, num))
            gaps.append({
                'after': prev_num,
                'before': num,
                'missing': missing
            })

# Report gaps
if gaps:
    print(f"⚠️  Found {len(gaps)} gaps in rule numbering:\n")
    for gap in gaps:
        print(f"   Gap between §{gap['after']} and §{gap['before']}")
        print(f"   Missing: {', '.join(f'§{n}' for n in gap['missing'])}\n")
else:
    print("✅ No gaps found in rule numbering!\n")

# Report duplicates (files with same rule number)
dup_nums = {k: v for k, v in duplicates.items() if len(v) > 1}
if dup_nums:
    print(f"ℹ️  Found {len(dup_nums)} rule numbers with multiple files (expected for different chapters):\n")
    for num in sorted(dup_nums.keys())[:10]:  # Show first 10
        print(f"   §{num}: {len(dup_nums[num])} files")
        for f in dup_nums[num]:
            print(f"      - {f}")
    if len(dup_nums) > 10:
        print(f"   ... and {len(dup_nums) - 10} more")
