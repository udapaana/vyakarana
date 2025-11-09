#!/usr/bin/env python3
"""Analyze extraction errors to find patterns"""

import json
from pathlib import Path
from collections import Counter

# Load status
with open("data/phase3_extraction_status.json") as f:
    status = json.load(f)

errors = status["errors"]
print(f"Total errors: {len(errors)}")
print()

# Group errors by range
error_rules = [int(k) for k in errors.keys()]
error_rules.sort()

print("Error distribution:")
print(f"  Rules 1-10: {sum(1 for r in error_rules if 1 <= r <= 10)}")
print(f"  Rules 11-20: {sum(1 for r in error_rules if 11 <= r <= 20)}")
print(f"  Rules 21-30: {sum(1 for r in error_rules if 21 <= r <= 30)}")
print(f"  Rules 31-40: {sum(1 for r in error_rules if 31 <= r <= 40)}")
print(f"  Rules 41-50: {sum(1 for r in error_rules if 41 <= r <= 50)}")
print(f"  Rules 51-65: {sum(1 for r in error_rules if 51 <= r <= 65)}")
print(f"  Rules 66+: {sum(1 for r in error_rules if r > 65)}")
print()

# Check if sequential
print("Error rules:")
consecutive_ranges = []
start = error_rules[0]
end = error_rules[0]

for i in range(1, len(error_rules)):
    if error_rules[i] == end + 1:
        end = error_rules[i]
    else:
        if start == end:
            consecutive_ranges.append(f"§{start}")
        else:
            consecutive_ranges.append(f"§{start}-{end}")
        start = error_rules[i]
        end = error_rules[i]

if start == end:
    consecutive_ranges.append(f"§{start}")
else:
    consecutive_ranges.append(f"§{start}-{end}")

print("  " + ", ".join(consecutive_ranges))
print()

# Check for patterns in page numbers
page_starts = [errors[str(r)]["page_start"] for r in error_rules]
print("Page start distribution:")
print(f"  Min page: {min(page_starts)}")
print(f"  Max page: {max(page_starts)}")
print(f"  Most common pages: {Counter(page_starts).most_common(5)}")
print()

# Sample a few errors
print("Sample errors (first 5):")
for rule_num in error_rules[:5]:
    err = errors[str(rule_num)]
    print(f"  §{rule_num}: page {err['page_start']} - {err['error']}")
