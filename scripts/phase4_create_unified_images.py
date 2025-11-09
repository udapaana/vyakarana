#!/usr/bin/env python3
"""
Phase 4: Create unified image set mapped to internal page numbers

This script:
1. Reads OCR files to extract internal page number mappings
2. Creates a gap-free image set using best available source
3. Renames images to match internal page numbers
4. Documents the mapping for reference
"""

import re
import shutil
from pathlib import Path
from collections import defaultdict

# Directories
OCR_DIR = Path("phase1_ocr/sources/official_1931")
IMAGE_SOURCES = {
    "official_1931": Path("phase1_ocr/images/official_1931"),
    "dli_2015": Path("phase1_ocr/images/dli_2015"),
}
OUTPUT_DIR = Path("phase4_images")

def extract_internal_page(ocr_file: Path) -> int:
    """Extract internal page number from OCR file"""
    try:
        content = ocr_file.read_text(encoding='utf-8', errors='ignore')
        # Look for [Internal page: NNN]
        match = re.search(r'\[Internal page:\s*(\d+)\]', content)
        if match:
            return int(match.group(1))
    except:
        pass
    return None

def build_page_mapping():
    """Build mapping of external page -> internal page"""
    mapping = {}
    
    for ocr_file in sorted(OCR_DIR.glob("*.txt")):
        external_page = int(ocr_file.stem)
        internal_page = extract_internal_page(ocr_file)
        
        if internal_page:
            mapping[external_page] = internal_page
    
    return mapping

def find_best_image(external_page: int) -> tuple:
    """Find best available image for an external page"""
    # Priority: official_1931 > dli_2015
    for source_name in ["official_1931", "dli_2015"]:
        source_dir = IMAGE_SOURCES[source_name]
        
        # Try different naming patterns
        patterns = [
            f"{external_page:03d}.png",
            f"page_{external_page:03d}.png",
            f"{external_page:03d}.jpg",
            f"page_{external_page:03d}.jpg",
        ]
        
        for pattern in patterns:
            img_file = source_dir / pattern
            if img_file.exists():
                return (img_file, source_name)
    
    return (None, None)

def create_unified_images():
    """Create unified image directory with internal page numbering"""
    
    print("=" * 70)
    print("PHASE 4: UNIFIED IMAGE CREATION")
    print("=" * 70)
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    print("\n1. Building page number mapping...")
    page_mapping = build_page_mapping()
    print(f"   Mapped {len(page_mapping)} pages")
    
    print("\n2. Copying and renaming images...")
    
    stats = {
        "official_1931": 0,
        "dli_2015": 0,
        "missing": 0,
    }
    
    mapping_log = []
    
    for external_page, internal_page in sorted(page_mapping.items()):
        img_file, source = find_best_image(external_page)
        
        if img_file:
            # Copy to output with internal page number
            output_file = OUTPUT_DIR / f"{internal_page:03d}.png"
            shutil.copy2(img_file, output_file)
            
            stats[source] += 1
            mapping_log.append({
                "internal": internal_page,
                "external": external_page,
                "source": source,
                "original": img_file.name
            })
            
            if stats[source] % 100 == 0:
                print(f"   Processed {sum(stats.values())} images...")
        else:
            print(f"   WARNING: No image found for external {external_page} (internal {internal_page})")
            stats["missing"] += 1
            mapping_log.append({
                "internal": internal_page,
                "external": external_page,
                "source": "MISSING",
                "original": None
            })
    
    print(f"\n3. Creating mapping documentation...")
    
    # Write mapping file
    mapping_file = OUTPUT_DIR / "PAGE_MAPPING.txt"
    with mapping_file.open('w') as f:
        f.write("PHASE 4 IMAGE MAPPING\n")
        f.write("=" * 70 + "\n\n")
        f.write("Internal | External | Source        | Original File\n")
        f.write("-" * 70 + "\n")
        
        for entry in mapping_log:
            orig = entry['original'] or 'MISSING'
            f.write(f"{entry['internal']:8} | {entry['external']:8} | {entry['source']:13} | {orig}\n")
    
    # Write summary
    summary_file = OUTPUT_DIR / "README.md"
    with summary_file.open('w') as f:
        f.write("# Phase 4: Unified Images\n\n")
        f.write("This directory contains a unified, gap-free set of page images for\n")
        f.write("Kale's Higher Sanskrit Grammar, renamed to match internal page numbers.\n\n")
        f.write("## Image Sources\n\n")
        f.write(f"- **official_1931**: {stats['official_1931']} images\n")
        f.write(f"- **dli_2015**: {stats['dli_2015']} images\n")
        f.write(f"- **Missing**: {stats['missing']} images\n")
        f.write(f"- **TOTAL**: {sum([stats['official_1931'], stats['dli_2015']])} images\n\n")
        f.write("## Naming Convention\n\n")
        f.write("Images are named `NNN.png` where NNN is the **internal page number**\n")
        f.write("as shown at the top of each page in the original text.\n\n")
        f.write("## Priority\n\n")
        f.write("When both sources had an image for the same page:\n")
        f.write("1. official_1931 (higher quality) was preferred\n")
        f.write("2. dli_2015 was used as fallback\n\n")
        f.write("## Page Mapping\n\n")
        f.write("See `PAGE_MAPPING.txt` for complete external -> internal page mapping.\n")
    
    print("\n" + "=" * 70)
    print("PHASE 4 COMPLETE")
    print("=" * 70)
    print(f"  Images from official_1931: {stats['official_1931']}")
    print(f"  Images from dli_2015:      {stats['dli_2015']}")
    print(f"  Missing images:            {stats['missing']}")
    print(f"  TOTAL:                     {sum([stats['official_1931'], stats['dli_2015']])}")
    print("=" * 70)
    print(f"\nImages saved to: {OUTPUT_DIR}/")
    print(f"Mapping saved to: {mapping_file}")
    print(f"README saved to: {summary_file}")

if __name__ == "__main__":
    create_unified_images()
