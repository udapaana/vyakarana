#!/usr/bin/env python3
"""
Scan the PDF to find which pages contain the missing rules
"""

import re
import PyPDF2
from pathlib import Path


def extract_text_from_page(pdf_reader, page_num):
    """Extract text from a PDF page"""
    try:
        page = pdf_reader.pages[page_num]
        return page.extract_text()
    except:
        return ""


def find_rules_in_text(text):
    """Find rule numbers in text (looking for § N pattern)"""
    # Look for patterns like "§ 7", "§ 8.", "§7", etc.
    patterns = [
        r"§\s*(\d+)",  # § 7
        r"§(\d+)",  # §7
    ]

    rules = set()
    for pattern in patterns:
        matches = re.findall(pattern, text)
        rules.update(int(m) for m in matches)

    return sorted(rules)


def main():
    pdf_path = Path("source/candidates/Official_7th_Edition_1931.pdf")

    if not pdf_path.exists():
        print(f"Error: PDF not found at {pdf_path}")
        return

    print("Opening PDF...")
    with open(pdf_path, "rb") as f:
        pdf_reader = PyPDF2.PdfReader(f)
        total_pages = len(pdf_reader.pages)
        print(f"Total PDF pages: {total_pages}\n")

        # Missing rules we're looking for
        missing_rules = [8, 9, 10, 32, 33, 81, 93, 121, 167, 168, 172, 173, 174, 175]

        print(f"Searching for missing rules: {missing_rules[:10]}...\n")
        print("=" * 70)

        found_mapping = {}

        # Search through all pages
        for page_num in range(total_pages):
            if page_num % 50 == 0:
                print(f"Scanning page {page_num}/{total_pages}...", end="\r")

            text = extract_text_from_page(pdf_reader, page_num)
            rules_on_page = find_rules_in_text(text)

            # Check if this page has any missing rules
            for rule in rules_on_page:
                if rule in missing_rules:
                    if page_num not in found_mapping:
                        found_mapping[page_num] = []
                    found_mapping[page_num].append(rule)

        print("\n" + "=" * 70)
        print("RESULTS: Pages containing missing rules")
        print("=" * 70 + "\n")

        if not found_mapping:
            print("❌ No missing rules found in PDF text extraction")
            print("   PDF might be scanned images without text layer")
            print("   Need to manually locate pages or use OCR on all pages")
        else:
            for pdf_page in sorted(found_mapping.keys()):
                rules = sorted(found_mapping[pdf_page])
                print(
                    f"PDF page {pdf_page:3d} (book page ~{pdf_page - 10:3d}): § {rules}"
                )

            print(f"\n✓ Found {len(found_mapping)} pages with missing rules")

            # Save to file
            with open("missing_pages_found.txt", "w") as out:
                out.write("PDF_PAGE,RULES\n")
                for pdf_page in sorted(found_mapping.keys()):
                    rules = ",".join(str(r) for r in sorted(found_mapping[pdf_page]))
                    out.write(f"{pdf_page},{rules}\n")

            print("✓ Saved to: missing_pages_found.txt")

            # Show extraction command
            print("\n" + "=" * 70)
            print("NEXT STEP: Extract these pages")
            print("=" * 70)
            pages_to_extract = sorted(found_mapping.keys())
            print(f"\nExtract PDF pages: {pages_to_extract[:20]}")
            if len(pages_to_extract) > 20:
                print(f"... and {len(pages_to_extract) - 20} more")


if __name__ == "__main__":
    main()
