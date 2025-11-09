#!/usr/bin/env python3
import re
import os

# Manual mappings for files that are difficult to parse automatically
MANUAL_MAPPINGS = {
    1: None,  # Title page
    2: None,  # Empty
    3: None,  # Title/publication page
    4: None,  # Copyright/registration page
    5: None,  # Dedication page
    6: None,  # Blank page marker
    10: None,  # Abbreviations (no page number)
    11: None,  # Preface (no page number on first page)
    12: None,  # Preface continuation
    13: None,  # Preface continuation
    14: None,  # Preface continuation
    15: None,  # Preface continuation
    17: None,  # Chapter 1 title page
    32: "13",  # Has 13' with apostrophe
    59: None,  # Need to check
    65: None,  # Need to check
    66: None,  # Need to check
    71: None,  # Need to check
    104: "83",  # Page with § 1 marker
    121: "95",  # § 159 section
    182: "165",  # Has page at end
    183: "166",  # Page number in content
    184: "167",  # Likely continuation
    185: "168",  # Likely continuation
    186: "169",  # Likely continuation
    187: "170",  # Likely continuation
    188: "171",  # Likely continuation
    189: "172",  # Likely continuation
    190: "173",  # Likely continuation
    210: None,  # Need to check
}

def extract_page_number(content):
    """
    Extract internal page number from OCR text.
    Looks for page numbers in headers/top of pages.
    """
    if not content or not content.strip():
        return None
    
    lines = content.split('\n')
    
    # Check first 15 lines for page numbers
    for i, line in enumerate(lines[:15]):
        line_stripped = line.strip()
        if not line_stripped:
            continue
        
        # Pattern 1: Roman numerals at start (i, ii, iii, iv, v, etc.)
        roman_match = re.match(r'^([ivxlcdm]+)$', line_stripped, re.IGNORECASE)
        if roman_match:
            return roman_match.group(1)
        
        # Pattern 2: Page number in brackets at start - "[ 135 ]" or "129 ]"
        bracket_match = re.match(r'^\[?\s*(\d+)\s*\]', line_stripped)
        if bracket_match:
            return bracket_match.group(1)
        
        # Pattern 3: Arabic numerals at start (including with special chars)
        arabic_match = re.match(r'^[·\s]*(\d+)\s*$', line_stripped)
        if arabic_match:
            return arabic_match.group(1)
        
        # Pattern 4: Page number with apostrophe at end of line
        if 'SANDHI' in line_stripped or 'GRAMMAR' in line_stripped:
            apostrophe_match = re.search(r'(\d+)\s*$', line_stripped)
            if apostrophe_match:
                return apostrophe_match.group(1)
        
        # Pattern 5: Page number with special character at start
        special_match = re.match(r'^[·\s]*(\d+)\s+[A-Z]', line_stripped)
        if special_match:
            return special_match.group(1)
        
        # Pattern 6: Page number in header with surrounding text (at start)
        header_match = re.match(r'^(\d+)\s+[A-Z]', line_stripped)
        if header_match:
            return header_match.group(1)
        
        # Pattern 7: Page number with section reference at start
        section_match = re.match(r'^(\d+)\s+.*\[\s*§', line_stripped)
        if section_match:
            return section_match.group(1)
        
        # Pattern 8: Section reference with page number at end
        section_end_match = re.match(r'^§[0-9\-]+\].*?(\d+)\s*$', line_stripped)
        if section_end_match:
            return section_end_match.group(1)
        
        # Pattern 9: Section reference with page number, various formats
        section_end_match2 = re.match(r'^§\s*[0-9\-]+\s*\].*?(\d+)\s*$', line_stripped)
        if section_end_match2:
            return section_end_match2.group(1)
        
        # Pattern 10: Page number at the end of a header line
        if re.search(r'[A-Z]', line_stripped):
            end_number = re.search(r'\s+(\d+)\s*$', line_stripped)
            if end_number:
                num = end_number.group(1)
                # Additional validation: should be separated by multiple spaces
                if re.search(r'\s{3,}' + num, line_stripped):
                    return num
        
        # Pattern 11: Standalone number within reasonable page range
        standalone = re.match(r'^(\d{1,3})$', line_stripped)
        if standalone and i > 0 and i < 5:
            num = int(standalone.group(1))
            if 1 <= num <= 300:
                return standalone.group(1)
    
    return None

def process_file(file_path, file_num):
    """
    Process a single file: read, extract page number, add header, write back.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if already has internal page marker
        if content.startswith('[Internal page:'):
            return None, "Already processed"
        
        # Check manual mapping first
        if file_num in MANUAL_MAPPINGS:
            page_num = MANUAL_MAPPINGS[file_num]
            if page_num is None:
                return None, "No page number (front matter/special)"
            else:
                new_content = f"[Internal page: {page_num}]\n{content}"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return page_num, "Updated (manual)"
        
        # Try automatic extraction
        page_num = extract_page_number(content)
        
        if page_num:
            new_content = f"[Internal page: {page_num}]\n{content}"
            with open(file_path, 'w', encoding='utf-8') as f:
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
        
        page_num, status = process_file(file_path, i)
        results[i] = (page_num, status)
        
        if "Updated" in status:
            print(f"File {i:03d}.txt: {status} with internal page {page_num}")
        elif status == "Already processed":
            print(f"File {i:03d}.txt: Already processed (skipped)")
        else:
            print(f"File {i:03d}.txt: {status}")
    
    print("=" * 80)
    print("\nSummary:")
    print(f"Total files processed: 210")
    
    updated = sum(1 for _, status in results.values() if "Updated" in status)
    already_done = sum(1 for _, status in results.values() if status == "Already processed")
    no_page = sum(1 for _, status in results.values() if "No page number" in status)
    errors = sum(1 for _, status in results.values() if "Error" in status or status == "File not found")
    
    print(f"Files updated: {updated}")
    print(f"Files already processed: {already_done}")
    print(f"Files with no page number: {no_page}")
    print(f"Errors/Not found: {errors}")
    
    total_with_pages = updated + already_done
    print(f"\nTotal files WITH page numbers: {total_with_pages}")
    
    # Print detailed list
    if no_page > 0:
        print("\nFiles without page numbers (front matter/special pages):")
        for file_num, (page_num, status) in results.items():
            if "No page number" in status:
                print(f"  {file_num:03d}.txt")

if __name__ == "__main__":
    main()
