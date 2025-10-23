#!/usr/bin/env python3
"""
Update placeholder files for rules that don't exist in the original book
"""

from pathlib import Path

# Rules that are genuinely missing from Kale's original numbering
NONEXISTENT_RULES = [134, 433, 631, 632, 635, 637]

rules_dir = Path('rules')

for rule_num in NONEXISTENT_RULES:
    filename = f"{rule_num:03d}.md"
    filepath = rules_dir / filename

    content = f"""---
rule: §{rule_num}
status: DOES NOT EXIST IN ORIGINAL
---

#### § {rule_num}. [This rule number does not exist in Kale's original text]

**Note:** This rule number is skipped in Kale's Sanskrit Grammar. The book jumps from:
- §133 → §135 (§134 skipped)
- §432 → §434 (§433 skipped)
- §630 → §638 (§631-637 skipped)

The original book contains 966 rules, not 972. These gaps are intentional in Kale's numbering system.

This placeholder file exists only to maintain sequential numbering in the digital archive.
"""

    filepath.write_text(content, encoding='utf-8')
    print(f"Updated §{rule_num} - marked as non-existent in original")

print(f"\n✓ Updated {len(NONEXISTENT_RULES)} placeholder files")
print(f"Actual rules in Kale's Grammar: 966")
print(f"Total files (including placeholders): 972")
