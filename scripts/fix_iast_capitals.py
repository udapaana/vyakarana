#!/usr/bin/env python3
"""
Fix capitalized letters inside @[...] IAST markers.
IAST transliteration is always lowercase - capitals don't transliterate to Devanagari.
"""

import re
from pathlib import Path

def lowercase_iast_content(match):
    """Lowercase the content inside @[...] markers"""
    content = match.group(1)
    return f'@[{content.lower()}]'

def fix_file(filepath):
    """Fix capitalized IAST in a single file"""
    content = filepath.read_text(encoding='utf-8')

    # Find all @[...] patterns with capital letters
    original = content

    # Replace @[Content] with @[content]
    content = re.sub(r'@\[([^\]]+)\]', lowercase_iast_content, content)

    if content != original:
        filepath.write_text(content, encoding='utf-8')
        return True
    return False

def main():
    final_dir = Path('final')

    print("="*60)
    print("Fixing capitalized IAST in @[...] markers")
    print("="*60)

    fixed_count = 0
    total_files = 0

    for md_file in sorted(final_dir.glob('*.md')):
        total_files += 1
        if fix_file(md_file):
            fixed_count += 1
            print(f"✓ Fixed {md_file.name}")

    print("\n" + "="*60)
    print(f"Complete: Fixed {fixed_count}/{total_files} files")
    print("="*60)

if __name__ == '__main__':
    main()
