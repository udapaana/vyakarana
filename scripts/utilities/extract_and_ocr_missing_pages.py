#!/usr/bin/env python3
"""
Extract missing PDF pages and prepare them for OCR
Step 1: Extract specific pages to separate PDFs
Step 2: Convert to images
Step 3: OCR with existing pipeline
"""

import PyPDF2
from pathlib import Path
import subprocess
import sys


def extract_pdf_pages(input_pdf, output_pdf, page_numbers):
    """Extract specific pages from PDF"""
    with open(input_pdf, "rb") as infile:
        reader = PyPDF2.PdfReader(infile)
        writer = PyPDF2.PdfWriter()

        for page_num in page_numbers:
            if page_num < len(reader.pages):
                writer.add_page(reader.pages[page_num])

        with open(output_pdf, "wb") as outfile:
            writer.write(outfile)


def pdf_to_images(pdf_path, output_dir):
    """Convert PDF to images using sips or pdf2image"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Try using macOS sips command
    try:
        result = subprocess.run(["sips", "--help"], capture_output=True, timeout=5)
        if result.returncode == 0:
            print("Using sips for conversion (macOS)")
            # sips can't directly convert PDF to PNG, need intermediate step
            print("⚠️  sips doesn't support PDF. Need alternative method.")
            return False
    except:
        pass

    return False


def main():
    # Configuration
    source_pdf = Path("source/candidates/Official_7th_Edition_1931.pdf")
    output_dir = Path("source/missing_pages")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Pages to extract (0-indexed in PyPDF2)
    # PDF page 23-24 = index 22-23
    missing_pages = {
        "pages_022-023_rules_7-10": [22, 23],  # § 7-10
        # Add more as we find them
    }

    print("=" * 70)
    print("EXTRACTING MISSING PDF PAGES")
    print("=" * 70 + "\n")

    for name, pages in missing_pages.items():
        output_pdf = output_dir / f"{name}.pdf"

        print(f"Extracting {name}...")
        print(f"  PDF pages: {[p + 1 for p in pages]} (indices: {pages})")

        try:
            extract_pdf_pages(source_pdf, output_pdf, pages)
            print(f"  ✓ Saved to: {output_pdf}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
            continue

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("\n1. Convert PDFs to images:")
    print(f"   Open {output_dir}/*.pdf in Preview")
    print(f"   Export as PNG images")
    print("\n2. Or use online tool:")
    print("   https://www.ilovepdf.com/pdf_to_jpg")
    print("\n3. Once you have images, run OCR:")
    print("   python3 scripts/google_vision_ocr.py source/missing_pages/*.png")
    print("   python3 scripts/claude_vision_ocr.py source/missing_pages/*.png")
    print("\n4. Structure the OCR output")
    print("\n5. Insert into structured_pages/ with correct numbering")


if __name__ == "__main__":
    main()
