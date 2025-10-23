#!/usr/bin/env python3
"""
Validate the complete extraction of all 972 rules
"""

import re
from pathlib import Path

def validate_extraction():
    rules_dir = Path('rules')

    print("="*60)
    print("VALIDATION REPORT - ALL 972 RULES")
    print("="*60 + "\n")

    # Check all files exist
    print("1. Checking file existence...")
    missing_files = []
    for i in range(1, 973):
        filename = f"{i:03d}.md"
        filepath = rules_dir / filename
        if not filepath.exists():
            missing_files.append(i)

    if missing_files:
        print(f"   ✗ MISSING FILES: {len(missing_files)}")
        print(f"     {', '.join(f'§{n}' for n in missing_files)}")
    else:
        print(f"   ✓ All 972 files exist")

    # Check YAML front matter format
    print("\n2. Checking YAML front matter...")
    yaml_errors = []
    for i in range(1, 973):
        filename = f"{i:03d}.md"
        filepath = rules_dir / filename
        if filepath.exists():
            content = filepath.read_text(encoding='utf-8')
            if not content.startswith('---\n'):
                yaml_errors.append(f"§{i}: Missing YAML front matter")
            elif not re.search(r'rule:\s*§\d+', content):
                yaml_errors.append(f"§{i}: Invalid rule field in YAML")

    if yaml_errors:
        print(f"   ✗ YAML ERRORS: {len(yaml_errors)}")
        for err in yaml_errors[:10]:  # Show first 10
            print(f"     {err}")
        if len(yaml_errors) > 10:
            print(f"     ... and {len(yaml_errors) - 10} more")
    else:
        print(f"   ✓ All files have valid YAML front matter")

    # Check for empty/too short content
    print("\n3. Checking content length...")
    short_files = []
    missing_content = []
    placeholders = []

    for i in range(1, 973):
        filename = f"{i:03d}.md"
        filepath = rules_dir / filename
        if filepath.exists():
            content = filepath.read_text(encoding='utf-8')

            # Check if it's a placeholder
            if 'NEEDS MANUAL EXTRACTION' in content:
                placeholders.append(i)
                continue

            # Extract body (after YAML)
            parts = content.split('---', 2)
            if len(parts) >= 3:
                body = parts[2].strip()

                if len(body) < 20:
                    short_files.append((i, len(body)))
                elif not body.startswith('####'):
                    missing_content.append(i)

    print(f"   Rules needing manual extraction: {len(placeholders)}")
    if placeholders:
        print(f"     {', '.join(f'§{n}' for n in placeholders)}")

    if short_files:
        print(f"   ✗ SHORT CONTENT: {len(short_files)} files")
        for rule_num, length in short_files[:10]:
            print(f"     §{rule_num}: only {length} chars")
        if len(short_files) > 10:
            print(f"     ... and {len(short_files) - 10} more")
    else:
        print(f"   ✓ No suspiciously short files")

    if missing_content:
        print(f"   ⚠ Missing rule header: {len(missing_content)} files")
        for rule_num in missing_content[:10]:
            print(f"     §{rule_num}")
        if len(missing_content) > 10:
            print(f"     ... and {len(missing_content) - 10} more")

    # Summary statistics
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    total_files = len(list(rules_dir.glob('*.md')))
    complete_rules = 972 - len(placeholders)

    print(f"Total files: {total_files}/972")
    print(f"Complete rules: {complete_rules}/972")
    print(f"Needs manual extraction: {len(placeholders)}/972")

    if total_files == 972 and len(yaml_errors) == 0:
        print("\n✓ STRUCTURE VALIDATION PASSED")
        if len(placeholders) > 0:
            print(f"⚠️  {len(placeholders)} rules need manual extraction from source")
        else:
            print("✓ ALL RULES COMPLETE!")
    else:
        print("\n✗ VALIDATION FAILED")

    # Check for duplicates (sanity check)
    print("\n4. Checking for duplicate rule numbers in content...")
    rule_numbers_seen = {}
    duplicates = []

    for filepath in sorted(rules_dir.glob('*.md')):
        content = filepath.read_text(encoding='utf-8')
        # Extract rule number from YAML
        match = re.search(r'rule:\s*§(\d+)', content)
        if match:
            rule_num = int(match.group(1))
            filename_num = int(filepath.stem)

            if rule_num != filename_num:
                duplicates.append(f"{filepath.name}: contains §{rule_num}")

    if duplicates:
        print(f"   ✗ MISMATCHES: {len(duplicates)}")
        for dup in duplicates[:10]:
            print(f"     {dup}")
    else:
        print(f"   ✓ All file names match rule numbers")

if __name__ == '__main__':
    validate_extraction()
