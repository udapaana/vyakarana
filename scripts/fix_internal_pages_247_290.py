#!/usr/bin/env python3
"""Fix internal_page numbers for pages 247-290 to match page_number"""

import re
from pathlib import Path

def fix_internal_page(page_num):
    """Fix internal_page for a single page"""
    file_path = Path(f"phase2_cleaned/page_{page_num:03d}.md")

    if not file_path.exists():
        print(f"⚠ Skipping {page_num}: file not found")
        return False

    content = file_path.read_text(encoding='utf-8')

    # Extract current internal_page value
    match = re.search(r'^internal_page: (\d+)$', content, re.MULTILINE)
    if not match:
        print(f"⚠ Page {page_num}: no internal_page found")
        return False

    current_internal = int(match.group(1))

    # Check if it needs fixing
    if current_internal == page_num:
        print(f"✓ Page {page_num}: already correct ({current_internal})")
        return True

    # Fix the internal_page to match page_number
    new_content = re.sub(
        r'^internal_page: \d+$',
        f'internal_page: {page_num}',
        content,
        count=1,
        flags=re.MULTILINE
    )

    file_path.write_text(new_content, encoding='utf-8')
    print(f"✓ Page {page_num}: fixed {current_internal} → {page_num}")
    return True

def main():
    print("Fixing internal_page values for pages 247-290...\n")

    fixed_count = 0
    for page_num in range(247, 291):
        if fix_internal_page(page_num):
            fixed_count += 1

    print(f"\n✓ Complete: processed {fixed_count}/44 pages")

if __name__ == "__main__":
    main()
