#!/usr/bin/env python3
import os

# Files that need manual page number addition
files_to_update = {
    59: "40",
    65: "46", 
    66: "47",
    71: "52",
    210: "196"
}

base_dir = "/Users/skmnktl/Downloads/ocr/phase1_ocr/sources/official_1931"

for file_num, page_num in files_to_update.items():
    file_path = os.path.join(base_dir, f"{file_num:03d}.txt")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if already has internal page marker
        if content.startswith('[Internal page:'):
            print(f"File {file_num:03d}.txt: Already has page number")
            continue
        
        # Add page number
        new_content = f"[Internal page: {page_num}]\n{content}"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"File {file_num:03d}.txt: Added internal page {page_num}")
    
    except Exception as e:
        print(f"File {file_num:03d}.txt: Error - {e}")

print("\nDone! All remaining files updated.")
