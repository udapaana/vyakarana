#!/usr/bin/env python3
"""Verify which downloaded sources are actually the 7th edition.

Extracts title pages and checks for edition information.

Following coding standards:
- Deep module: User runs script, gets verification results
- Comments explain why: Why we need to verify (different editions exist)
"""

from pathlib import Path
from pdf2image import convert_from_path
import sys


def extract_title_page(pdf_path: Path, output_path: Path) -> bool:
    """Extract title page from PDF for manual inspection.

    Why manual inspection: Edition info can appear in various formats,
    human verification is more reliable than OCR pattern matching.

    Args:
        pdf_path: Path to PDF file
        output_path: Where to save title page image

    Returns:
        True if successful, False otherwise
    """
    try:
        # Why pages 1-5: Title/copyright usually in first few pages
        images = convert_from_path(
            pdf_path,
            first_page=1,
            last_page=5,
            dpi=200  # Why 200 DPI: Readable for human verification
        )

        # Save all first 5 pages for inspection
        for i, img in enumerate(images, 1):
            page_output = output_path.parent / f"{output_path.stem}_page{i}.png"
            img.save(page_output)

        print(f"  ✓ Extracted {len(images)} pages to {output_path.parent}")
        return True

    except Exception as e:
        print(f"  ✗ Failed to extract: {e}")
        return False


def main():
    """Extract title pages from all candidate PDFs for verification."""
    print("="*70)
    print("Verifying 7th Edition Sources")
    print("="*70)
    print("\nExtracting title pages for manual verification...")
    print()

    source_dir = Path("source/candidates")
    output_dir = Path("verification")
    output_dir.mkdir(exist_ok=True)

    if not source_dir.exists():
        print(f"Error: {source_dir} not found")
        print("Run download_7th_edition_sources.py first")
        sys.exit(1)

    pdfs = list(source_dir.glob("*.pdf"))
    if not pdfs:
        print(f"Error: No PDFs found in {source_dir}")
        sys.exit(1)

    print(f"Found {len(pdfs)} PDF(s) to verify\n")

    for pdf_path in pdfs:
        print(f"Processing: {pdf_path.name}")
        output_path = output_dir / pdf_path.stem
        extract_title_page(pdf_path, output_path)
        print()

    print("="*70)
    print("Verification Images Ready")
    print("="*70)
    print(f"\nTitle pages saved to: {output_dir}/")
    print("\nManual verification needed:")
    print("  1. Open images in verification/ directory")
    print("  2. Check for '7th edition' or 'Seventh Edition' text")
    print("  3. Check publication year (7th ed. = 1931)")
    print("  4. Keep only verified 7th edition PDFs")
    print("\nExample edition markers to look for:")
    print("  - 'SEVENTH EDITION'")
    print("  - '7th Edition'")
    print("  - 'Revised and Enlarged' (often with 7th)")
    print("  - Publication year: 1931")


if __name__ == "__main__":
    main()
