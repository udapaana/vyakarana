#!/usr/bin/env python3
"""
Create placeholder files for the 8 missing rules that need manual extraction
"""

from pathlib import Path

MISSING_RULES = [134, 292, 433, 631, 632, 635, 637, 921]

rules_dir = Path('rules')

for rule_num in MISSING_RULES:
    filename = f"{rule_num:03d}.md"
    filepath = rules_dir / filename

    content = f"""---
rule: §{rule_num}
status: MISSING - NEEDS MANUAL EXTRACTION
---

#### § {rule_num}. [CONTENT MISSING FROM OCR - MANUAL EXTRACTION REQUIRED]

**Note:** This rule was not found in either:
- v7 processed markdown
- Raw OCR pages

This rule needs to be manually extracted from the original PDF or scanned images.

To complete this file:
1. Locate the original source (PDF/image)
2. Find § {rule_num}
3. Extract the complete rule text
4. Replace this placeholder with the actual content
5. Remove the 'status' field from the YAML front matter
"""

    filepath.write_text(content, encoding='utf-8')
    print(f"Created placeholder for §{rule_num}")

print(f"\n✓ Created {len(MISSING_RULES)} placeholder files")
print(f"Total files in rules/: {len(list(rules_dir.glob('*.md')))}")
