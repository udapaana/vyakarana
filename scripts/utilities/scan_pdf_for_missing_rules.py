#!/usr/bin/env python3
"""
Systematically scan PDF to find all pages containing missing rules
"""

import re
import PyPDF2
from pathlib import Path
from collections import defaultdict


def find_rules_in_text(text):
    """Find all § N patterns in text"""
    # Look for § followed by number
    matches = re.findall(r"§\s*(\d+)", text)
    return sorted(set(int(m) for m in matches if int(m) <= 972))


def main():
    # Missing rules we need to find
    missing_rules = [
        8,
        9,
        10,
        32,
        33,
        81,
        93,
        121,
        167,
        168,
        172,
        173,
        174,
        175,
        185,
        186,
        206,
        235,
        236,
        237,
        284,
        285,
        304,
        305,
        318,
        319,
        320,
        331,
        332,
        344,
        376,
        379,
        380,
        381,
        382,
        383,
        384,
        385,
        396,
        402,
        438,
        439,
        445,
        446,
        447,
        448,
        452,
        453,
        455,
        460,
        461,
        462,
        463,
        464,
        465,
        467,
        468,
        481,
        482,
        483,
        488,
        489,
        490,
        491,
        492,
        498,
        499,
        501,
        502,
        519,
        520,
        521,
        522,
        523,
        524,
        525,
        526,
        550,
        551,
        557,
        558,
        559,
        561,
        562,
        566,
        604,
        605,
        625,
        626,
        656,
        657,
        665,
        666,
        682,
        683,
        691,
        692,
        710,
        711,
        723,
        724,
        725,
        726,
        727,
        741,
        742,
        743,
        744,
        790,
        791,
        792,
        793,
        794,
        795,
        796,
        809,
        810,
        811,
        812,
        813,
        814,
        830,
        831,
        835,
        836,
        837,
        842,
        843,
        844,
        859,
        860,
        861,
        865,
        879,
        880,
        881,
        921,
        922,
        940,
        941,
        942,
        945,
        946,
        947,
        948,
        949,
        954,
        955,
        956,
        957,
        958,
        959,
        960,
        961,
        962,
        967,
        971,
        972,
    ]

    pdf_path = Path("source/candidates/Official_7th_Edition_1931.pdf")

    print("Scanning PDF for missing rules...")
    print(f"Looking for {len(missing_rules)} missing rules\n")

    with open(pdf_path, "rb") as f:
        pdf_reader = PyPDF2.PdfReader(f)
        total_pages = len(pdf_reader.pages)

        # Map: PDF page → rules found
        page_to_rules = defaultdict(list)
        # Map: rule → PDF page
        rule_to_page = {}

        # Scan pages (focus on pages 10-700 where grammar rules are)
        for pdf_page in range(10, min(700, total_pages)):
            if pdf_page % 20 == 0:
                print(f"Scanned {pdf_page}/{total_pages} pages...", end="\r")

            text = pdf_reader.pages[pdf_page].extract_text()
            rules = find_rules_in_text(text)

            for rule in rules:
                if rule in missing_rules:
                    page_to_rules[pdf_page].append(rule)
                    if rule not in rule_to_page:
                        rule_to_page[rule] = pdf_page

        print(f"\nScanned {total_pages} pages\n")

        # Show results
        print("=" * 70)
        print("FOUND PAGES CONTAINING MISSING RULES")
        print("=" * 70 + "\n")

        if not page_to_rules:
            print("❌ No missing rules found via text extraction")
            print("   PDF may be image-only, need OCR approach")
            return

        # Sort by PDF page
        for pdf_page in sorted(page_to_rules.keys()):
            rules = sorted(set(page_to_rules[pdf_page]))
            # Estimate book page (approximately PDF page - 11 for front matter)
            book_page_est = pdf_page - 11
            print(f"PDF page {pdf_page:3d} (≈ book page {book_page_est:3d}): § {rules}")

        # Show which rules are still missing
        found_rules = set(rule_to_page.keys())
        still_missing = sorted(set(missing_rules) - found_rules)

        print(f"\n✓ Found {len(found_rules)} out of {len(missing_rules)} missing rules")

        if still_missing:
            print(f"\n⚠️  Still missing {len(still_missing)} rules:")
            print(f"   {still_missing[:30]}")
            if len(still_missing) > 30:
                print(f"   ... and {len(still_missing) - 30} more")

        # Save results
        output_file = Path("missing_pages_to_extract.txt")
        with open(output_file, "w") as out:
            out.write("# PDF pages to extract and OCR\n")
            out.write(
                f"# Found {len(page_to_rules)} pages with {len(found_rules)} missing rules\n\n"
            )

            for pdf_page in sorted(page_to_rules.keys()):
                rules = sorted(set(page_to_rules[pdf_page]))
                out.write(f"{pdf_page}\t§ {rules}\n")

        print(f"\n✓ Saved to: {output_file}")

        # Generate extraction command
        pages = sorted(page_to_rules.keys())
        print("\n" + "=" * 70)
        print("NEXT STEP: Extract these PDF pages")
        print("=" * 70)
        print(f"\nPages to extract: {pages[:20]}")
        if len(pages) > 20:
            print(f"... and {len(pages) - 20} more")

        print(f"\nCommand to extract (example):")
        print(
            f"  pdftk source/candidates/Official_7th_Edition_1931.pdf cat {' '.join(map(str, pages[:5]))} output missing_pages.pdf"
        )


if __name__ == "__main__":
    main()
