#!/usr/bin/env python3
"""Quick script to OCR specific missing pages with Claude."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from claude_vision_ocr import ocr_pdf_page

# Configuration
PDF_PATH = Path("/Users/skmnktl/Downloads/ocr/data/kale_higher_sanskrit_grammar.pdf")
CLAUDE_OUTPUT = Path("/Users/skmnktl/Downloads/ocr/ocr_output/claude")

# Pages missing Claude OCR
MISSING_PAGES = [101, 448]

def main():
    print("="*70)
    print("OCR Missing Pages with Claude")
    print("="*70)

    for page_num in MISSING_PAGES:
        print(f"\n[{page_num}] Processing page {page_num}...")
        try:
            result = ocr_pdf_page(
                PDF_PATH,
                page_num,
                CLAUDE_OUTPUT,
                preprocess=True
            )
            print(f"  ✅ Success: {len(result['text'])} chars")
        except Exception as e:
            print(f"  ❌ Failed: {e}")

    print("\n" + "="*70)
    print("Done!")

if __name__ == "__main__":
    main()
