#!/usr/bin/env python3
"""
Identify which book pages are missing from structured_pages/
and need to be OCR'd from the source PDF.
"""

import re
from pathlib import Path
from collections import defaultdict


def main():
    # Scan existing structured pages
    all_rules_found = set()
    book_page_to_rules = defaultdict(list)

    for page_file in sorted(Path("structured_pages").glob("page_*.md")):
        with open(page_file) as f:
            content = f.read(1500)

        # Extract book page number
        page_match = re.search(r"^page:\s*(\d+)", content, re.MULTILINE)
        if not page_match:
            continue
        book_page = int(page_match.group(1))

        # Extract rule numbers
        rule_matches = re.findall(r'rule:\s*["\[]?\s*§?\s*(\d+)(?:-(\d+))?', content)
        for match in rule_matches:
            start = int(match[0])
            end = int(match[1]) if match[1] else start
            for rule_num in range(start, end + 1):
                all_rules_found.add(rule_num)
                book_page_to_rules[book_page].append(rule_num)

    # Find missing rules
    expected_rules = set(range(1, 973))  # § 1 through § 972
    missing_rules = sorted(expected_rules - all_rules_found)

    print("=" * 70)
    print("MISSING RULE ANALYSIS")
    print("=" * 70)
    print(f"\nTotal rules found: {len(all_rules_found)}")
    print(f"Total rules missing: {len(missing_rules)}")
    print(f"\nMissing rules: {missing_rules[:50]}")
    if len(missing_rules) > 50:
        print(f"... and {len(missing_rules) - 50} more")

    # Estimate which book pages we need
    print("\n" + "=" * 70)
    print("ESTIMATED MISSING BOOK PAGES")
    print("=" * 70)

    # Group missing rules into ranges
    if missing_rules:
        print("\nMissing rule ranges (need to find these in PDF):")

        ranges = []
        start = missing_rules[0]
        prev = start

        for rule in missing_rules[1:]:
            if rule - prev > 1:
                ranges.append((start, prev))
                start = rule
            prev = rule
        ranges.append((start, prev))

        for start, end in ranges:
            if start == end:
                print(f"  § {start}")
            else:
                print(f"  § {start}-{end}")

    # Show first gap in detail (§ 7-10)
    print("\n" + "=" * 70)
    print("FIRST GAP DETAIL: § 7, 8, 9, 10")
    print("=" * 70)
    print("\nContext from existing pages:")
    print("  Book page 13: § 5-6")
    print("  Book page 14: § 11-12")
    print("\n→ We need the book page(s) between page 13 and 14")
    print("→ This should contain § 7, 8, 9, 10")
    print("\nAction: Look at PDF pages around book page 13-14")
    print("        (Note: PDF page numbers may differ from book page numbers)")

    # Save missing rules to file
    output_file = Path("missing_rules.txt")
    with open(output_file, "w") as f:
        f.write(f"Total missing: {len(missing_rules)}\n\n")
        f.write("Missing rules:\n")
        for rule in missing_rules:
            f.write(f"§ {rule}\n")

    print(f"\n✓ Saved full list to: {output_file}")

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("1. Open source/candidates/Official_7th_Edition_1931.pdf")
    print("2. Find the missing book pages manually")
    print("3. Extract those specific PDF pages")
    print("4. Run OCR on extracted pages")
    print("5. Structure and insert into structured_pages/")


if __name__ == "__main__":
    main()
