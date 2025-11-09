#!/usr/bin/env python3
import re
import os


def extract_page_number(content):
    """
    Extract internal page number from OCR text.
    Looks for page numbers in headers/top of pages.
    """
    if not content or not content.strip():
        return None

    lines = content.split("\n")

    # Check first 10 lines for page numbers
    for i, line in enumerate(lines[:10]):
        line_stripped = line.strip()
        if not line_stripped:
            continue

        # Pattern 1: Roman numerals at start (i, ii, iii, iv, v, etc.)
        roman_match = re.match(r"^([ivxlcdm]+)$", line_stripped, re.IGNORECASE)
        if roman_match:
            return roman_match.group(1)

        # Pattern 2: Page number in brackets at start - "[ 135 ]" or "129 ]"
        bracket_match = re.match(r"^[\[\s]*(\d+)\s*\]", line_stripped)
        if bracket_match:
            return bracket_match.group(1)

        # Pattern 3: Arabic numerals at start (including with special chars like ·)
        arabic_match = re.match(r"^[·\s]*(\d+)\s*$", line_stripped)
        if arabic_match:
            return arabic_match.group(1)

        # Pattern 4: Page number with special character at start
        # e.g., "·12                        SANSKRIT GRAMMAR."
        special_match = re.match(r"^[·\s]*(\d+)\s+[A-Z]", line_stripped)
        if special_match:
            return special_match.group(1)

        # Pattern 5: Page number in header with surrounding text (at start)
        # e.g., "80                    HIGHER SANSKRIT GRAMMAR."
        header_match = re.match(r"^(\d+)\s+[A-Z]", line_stripped)
        if header_match:
            return header_match.group(1)

        # Pattern 6: Page number with section reference at start
        section_match = re.match(r"^(\d+)\s+.*\[\s*§", line_stripped)
        if section_match:
            return section_match.group(1)

        # Pattern 7: Section reference with page number at end
        # e.g., "§9-10]                        THE ALPHABET.                       7"
        section_end_match = re.match(r"^§[0-9\-]+\].*?(\d+)\s*$", line_stripped)
        if section_end_match:
            return section_end_match.group(1)

        # Pattern 8: Section reference with page number, various formats
        # e.g., "§ 130-132 ]                    DECLENSION.                    81"
        section_end_match2 = re.match(r"^§\s*[0-9\-]+\s*\].*?(\d+)\s*$", line_stripped)
        if section_end_match2:
            return section_end_match2.group(1)

        # Pattern 9: Page number at the end of a header line (not just section headers)
        # Look for lines with mostly spaces and capital letters ending with a number
        if re.search(r"[A-Z]", line_stripped):
            end_number = re.search(r"\s+(\d+)\s*$", line_stripped)
            if end_number:
                num = end_number.group(1)
                # Additional validation: should be separated by multiple spaces
                if re.search(r"\s{3,}" + num + r"\s*$", line_stripped):
                    return num

        # Pattern 10: Just page number at end preceded by section/word
        # e.g., "SANSKRIT GRAMMAR.                                                  [ § 340"
        # Look in next line for the page number
        if "§" in line_stripped and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line and next_line.isdigit():
                return next_line

    return None


def process_file(file_path):
    """
    Process a single file: read, extract page number, add header, write back.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Skip if already has internal page marker
        if content.startswith("[Internal page:"):
            return None, "Already processed"

        page_num = extract_page_number(content)

        if page_num:
            new_content = f"[Internal page: {page_num}]\n{content}"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return page_num, "Updated"
        else:
            return None, "No page number found"

    except Exception as e:
        return None, f"Error: {str(e)}"


def main():
    base_dir = "/Users/skmnktl/Downloads/ocr/phase1_ocr/sources/official_1931"
    results = {}

    print("Processing files...")
    print("=" * 80)

    for i in range(1, 211):
        file_path = os.path.join(base_dir, f"{i:03d}.txt")

        if not os.path.exists(file_path):
            results[i] = (None, "File not found")
            continue

        page_num, status = process_file(file_path)
        results[i] = (page_num, status)

        if status == "Updated":
            print(f"File {i:03d}.txt: Updated with internal page {page_num}")
        elif status == "Already processed":
            print(f"File {i:03d}.txt: Already processed (skipped)")
        elif status == "No page number found":
            print(
                f"File {i:03d}.txt: No page number found (empty or unrecognized format)"
            )
        else:
            print(f"File {i:03d}.txt: {status}")

    print("=" * 80)
    print("\nSummary:")
    print(f"Total files processed: 210")

    updated = sum(1 for _, status in results.values() if status == "Updated")
    already_done = sum(
        1 for _, status in results.values() if status == "Already processed"
    )
    no_page = sum(
        1 for _, status in results.values() if status == "No page number found"
    )
    errors = sum(
        1
        for _, status in results.values()
        if "Error" in status or status == "File not found"
    )

    print(f"Files updated: {updated}")
    print(f"Files already processed: {already_done}")
    print(f"Files with no page number: {no_page}")
    print(f"Errors/Not found: {errors}")

    # Print detailed list of files without page numbers for review
    if no_page > 0:
        print("\nFiles without page numbers:")
        for file_num, (page_num, status) in results.items():
            if status == "No page number found":
                print(f"  {file_num:03d}.txt")


if __name__ == "__main__":
    main()
