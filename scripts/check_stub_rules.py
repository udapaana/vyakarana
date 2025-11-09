#!/usr/bin/env python3
"""Check what stub rules actually contain"""

from pathlib import Path

PHASE3_DIR = Path("phase3_rules")

# Sample of "stub" rules from audit
stub_samples = [5, 7, 11, 14, 16, 29, 31, 35, 37, 47, 48, 51, 53, 56, 58]

print("=" * 80)
print("CHECKING 'STUB' RULES")
print("=" * 80)

for rule_num in stub_samples:
    file_path = PHASE3_DIR / f"rule_{rule_num:03d}.md"

    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')

        # Split frontmatter and body
        parts = content.split('---', 2)
        if len(parts) >= 3:
            body = parts[2]
        else:
            body = content

        # Count non-empty, non-comment lines
        body_lines = [line for line in body.split('\n')
                     if line.strip() and not line.strip().startswith('<!--')]

        print(f"\n§{rule_num} - {len(body_lines)} lines, {len(body.strip())} chars")
        print(f"Content preview:")
        all_lines = body.strip().split('\n')
        preview_lines = all_lines[:5]
        for line in preview_lines:
            print(f"  {line[:76]}")
        if len(all_lines) > 5:
            total_lines = len(all_lines)
            print(f"  ... ({total_lines} total lines)")

    except Exception as e:
        print(f"\n§{rule_num} - ERROR: {e}")

print("\n" + "=" * 80)
