#!/usr/bin/env python3
"""
Add internal_page mappings to Stage 3A rules for human proofreading.

This adds a mapping from sequence page numbers (001, 002, etc.) to
the actual printed page numbers in the book (i, ii, 1, 2, etc.) so
that proofreaders can reference the original book pages.
"""

import re
import yaml
from pathlib import Path


PHASE2_DIR = Path("/Users/skmnktl/Downloads/ocr/phase2_cleaned")
PHASE3A_DIR = Path("/Users/skmnktl/Downloads/ocr/phase3_rules/core/raw")


def get_page_mappings():
    """Build a mapping of page_number -> internal_page from Phase 2"""
    mappings = {}

    for page_file in sorted(PHASE2_DIR.glob("page_*.md")):
        content = page_file.read_text(encoding="utf-8")

        # Extract frontmatter
        match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
        if not match:
            continue

        fm = yaml.safe_load(match.group(1))
        page_num = fm.get("page_number")
        internal_page = fm.get("internal_page")

        if page_num and internal_page:
            mappings[page_num] = str(internal_page)

    return mappings


def update_rule_file(rule_file, page_mappings):
    """Add internal_pages field to a rule file"""

    content = rule_file.read_text(encoding="utf-8")

    # Extract frontmatter and body
    match = re.match(r"^(---\n)(.*?)(\n---\n)(.*)$", content, re.DOTALL)
    if not match:
        print(f"  WARNING: Could not parse {rule_file.name}")
        return False

    fm_start = match.group(1)
    fm_content = match.group(2)
    fm_end = match.group(3)
    body = match.group(4)

    # Parse frontmatter
    fm = yaml.safe_load(fm_content)

    # Get source pages
    source_pages = fm.get("source_pages", [])
    if not source_pages:
        return False

    # Map to internal pages
    internal_pages = []
    for page_num_str in source_pages:
        page_num = int(page_num_str)
        if page_num in page_mappings:
            internal_pages.append(page_mappings[page_num])
        else:
            print(f"  WARNING: No mapping for page {page_num}")
            internal_pages.append(f"page_{page_num_str}")

    # Add internal_pages field
    fm["internal_pages"] = internal_pages

    # Also add image_files for direct reference
    fm["image_files"] = [f"{p}.png" for p in source_pages]

    # Reconstruct file
    new_content = fm_start
    new_content += yaml.dump(
        fm, default_flow_style=False, allow_unicode=True, sort_keys=False
    )
    new_content += fm_end
    new_content += body

    rule_file.write_text(new_content, encoding="utf-8")
    return True


def main():
    print("\n" + "=" * 70)
    print("ADDING INTERNAL PAGE MAPPINGS TO STAGE 3A RULES")
    print("=" * 70 + "\n")

    # Build page mappings
    print("Building page number mappings from Phase 2...")
    page_mappings = get_page_mappings()
    print(f"  ✓ Loaded {len(page_mappings)} page mappings\n")

    # Update all rule files
    rule_files = sorted(PHASE3A_DIR.glob("rule_*.md"))
    updated = 0
    skipped = 0

    for rule_file in rule_files:
        if update_rule_file(rule_file, page_mappings):
            updated += 1
        else:
            skipped += 1

    print("\n" + "=" * 70)
    print(f"Updated: {updated} rules")
    print(f"Skipped: {skipped} rules")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
