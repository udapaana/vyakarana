#!/usr/bin/env python3
"""
Phase 2 Corrections: Fix Known OCR Gaps

This script applies manual corrections to Phase 2 cleaned files based on
verified source material (Archive.org) to fix OCR page boundary gaps.

Each correction is documented with:
- Page number
- Issue description
- Source verification
- Exact correction applied
"""

import re
from pathlib import Path

PHASE2_DIR = Path("/Users/skmnktl/Downloads/ocr/phase2_cleaned")

# Corrections database
# Format: {page_number: [(find_text, replace_text, description, source)]}
CORRECTIONS = {
    10: [
        (
            "Since short vowels include the long and the protracted vowels (See § 3. a.) another इत् 'ट्' is generally employed to mark a",
            "Since short vowels include the long and the protracted vowels (See § 3. a.) another इत् 'ट्' is generally employed to mark a particular vowel",
            "Complete incomplete sentence at page boundary",
            "Archive.org: https://archive.org/stream/xMqc_a-higher-sanskrit-grammar-by-moreshwar-ram-chandra-kale-1931-d-v-mulgaokar/",
        ),
    ],
}


def apply_corrections(page_num, dry_run=True):
    """Apply corrections to a specific page"""

    if page_num not in CORRECTIONS:
        return None

    page_file = PHASE2_DIR / f"page_{page_num:03d}.md"

    if not page_file.exists():
        return f"ERROR: {page_file} does not exist"

    content = page_file.read_text(encoding="utf-8")
    original_content = content

    corrections_applied = []

    for find_text, replace_text, description, source in CORRECTIONS[page_num]:
        if find_text in content:
            content = content.replace(find_text, replace_text)
            corrections_applied.append(
                {
                    "description": description,
                    "source": source,
                    "find": find_text[:50] + "..."
                    if len(find_text) > 50
                    else find_text,
                    "replace": replace_text[:50] + "..."
                    if len(replace_text) > 50
                    else replace_text,
                }
            )
        else:
            return f"WARNING: Could not find text to replace on page {page_num}"

    if corrections_applied:
        if not dry_run:
            page_file.write_text(content, encoding="utf-8")

        return {
            "page": page_num,
            "corrections": corrections_applied,
            "dry_run": dry_run,
        }

    return None


def main():
    """Apply all corrections"""

    print("=" * 70)
    print("PHASE 2 CORRECTIONS - Fixing Known OCR Gaps")
    print("=" * 70)
    print()

    # First, dry run to show what would be changed
    print("DRY RUN - Showing proposed changes:\n")

    for page_num in sorted(CORRECTIONS.keys()):
        result = apply_corrections(page_num, dry_run=True)

        if isinstance(result, dict):
            print(f"Page {result['page']:03d}:")
            for corr in result["corrections"]:
                print(f"  ✓ {corr['description']}")
                print(f"    Find:    {corr['find']}")
                print(f"    Replace: {corr['replace']}")
                print(f"    Source:  {corr['source']}")
            print()
        elif result:
            print(f"Page {page_num:03d}: {result}\n")

    # Ask for confirmation
    response = input("Apply these corrections? (yes/no): ").strip().lower()

    if response != "yes":
        print("Aborted.")
        return

    # Apply corrections
    print("\nApplying corrections...\n")

    for page_num in sorted(CORRECTIONS.keys()):
        result = apply_corrections(page_num, dry_run=False)

        if isinstance(result, dict):
            print(
                f"✓ Page {result['page']:03d}: {len(result['corrections'])} correction(s) applied"
            )
        elif result:
            print(f"✗ Page {page_num:03d}: {result}")

    print("\n" + "=" * 70)
    print("Corrections complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
