#!/usr/bin/env python3
import re
from pathlib import Path

# Get all rules from v7 source
v7_file = Path("output/kales_sanskrit_grammar_v7.md")
with open(v7_file, 'r') as f:
    content = f.read()

# Find all § markers in v7
source_rules = set()
for match in re.finditer(r'#### § (\d+)\.', content):
    source_rules.add(int(match.group(1)))

# Get all extracted rules
v8_dir = Path("v8_sections")
extracted_rules = set()
for f in v8_dir.rglob("s*.md"):
    match = re.match(r's(\d+)\.md', f.name)
    if match:
        extracted_rules.add(int(match.group(1)))

print(f"📊 Source file contains: {len(source_rules)} unique rule numbers")
print(f"📁 Extracted files: {len(extracted_rules)} rules")
print()

# Rules in source but not extracted
missing_from_extraction = source_rules - extracted_rules
if missing_from_extraction:
    print(f"❌ Rules in source but NOT extracted ({len(missing_from_extraction)}):")
    for r in sorted(missing_from_extraction)[:20]:
        print(f"   §{r}")
    if len(missing_from_extraction) > 20:
        print(f"   ... and {len(missing_from_extraction) - 20} more")
else:
    print("✅ All source rules have been extracted!")

print()

# Rules extracted but not in source (shouldn't happen)
extra_in_extraction = extracted_rules - source_rules
if extra_in_extraction:
    print(f"⚠️  Rules extracted but NOT in source ({len(extra_in_extraction)}):")
    for r in sorted(extra_in_extraction):
        print(f"   §{r}")
else:
    print("✅ No extra rules in extraction!")

print()

# Identify intentional gaps in the source
if source_rules:
    min_rule = min(source_rules)
    max_rule = max(source_rules)
    all_possible = set(range(min_rule, max_rule + 1))
    intentional_gaps = all_possible - source_rules
    
    if intentional_gaps:
        print(f"ℹ️  Intentional gaps in original book ({len(intentional_gaps)} rule numbers never written):")
        
        # Group consecutive gaps
        gaps = sorted(intentional_gaps)
        ranges = []
        start = gaps[0]
        end = gaps[0]
        
        for i in range(1, len(gaps)):
            if gaps[i] == end + 1:
                end = gaps[i]
            else:
                if start == end:
                    ranges.append(f"§{start}")
                else:
                    ranges.append(f"§{start}-§{end}")
                start = gaps[i]
                end = gaps[i]
        
        # Add last range
        if start == end:
            ranges.append(f"§{start}")
        else:
            ranges.append(f"§{start}-§{end}")
        
        for r in ranges[:30]:
            print(f"   {r}")
        if len(ranges) > 30:
            print(f"   ... and {len(ranges) - 30} more")
