#!/usr/bin/env python3
import re
from pathlib import Path

print("Complete rule validation with range expansion...\n")

all_rules = set()

for page_file in Path("phase2_structured").glob("page_*.md"):
    with open(page_file) as f:
        content = f.read()

    # Find rule: field in YAML
    yaml_match = re.search(r"^rule:\s*(.+?)$", content, re.MULTILINE)
    if not yaml_match:
        continue

    rule_text = yaml_match.group(1).strip("\"'")

    # Parse different formats:
    # "§ 5-6" -> 5, 6
    # "§§ 31-36" -> 31, 32, 33, 34, 35, 36
    # "§ 12" -> 12

    # Find all range patterns
    ranges = re.findall(r"§+\s*(\d+)(?:\s*[-–]\s*(\d+))?", rule_text)

    for match in ranges:
        start = int(match[0])
        end = int(match[1]) if match[1] else start

        # Add all rules in range
        for rule in range(start, end + 1):
            if 1 <= rule <= 972:
                all_rules.add(rule)

# Validate
expected = set(range(1, 973))
found = all_rules
missing = sorted(expected - found)

print(f"Total rules found: {len(found)}")
print(f"Expected: 972")
print(f"Still missing: {len(missing)}")

if missing:
    print(f"\nMissing rules: {missing[:50]}")
    if len(missing) > 50:
        print(f"... and {len(missing) - 50} more")

    with open("final_missing_rules.txt", "w") as f:
        f.write(f"Missing after structuring phase: {len(missing)} rules\n\n")
        for rule in missing:
            f.write(f"§ {rule}\n")
    print(f"\n✓ Saved to: final_missing_rules.txt")
else:
    print("\n🎉 ALL 972 RULES PRESENT!")
