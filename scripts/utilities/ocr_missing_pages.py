#!/usr/bin/env python3
"""
OCR missing pages 24-25 from PDF using Claude Vision API
"""

import os
import sys
import base64
import json
from pathlib import Path
from anthropic import Anthropic


def pdf_page_to_base64(pdf_path, page_number):
    """
    Extract a page from PDF and convert to base64 image
    Uses PyMuPDF (fitz) for rendering
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("ERROR: PyMuPDF (fitz) not installed")
        print("Install with: pip install PyMuPDF")
        sys.exit(1)

    doc = fitz.open(pdf_path)
    page = doc[page_number]

    # Render page to image at high DPI for better OCR
    pix = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72))

    # Convert to PNG bytes
    img_bytes = pix.tobytes("png")

    # Encode to base64
    img_base64 = base64.standard_b64encode(img_bytes).decode("utf-8")

    doc.close()
    return img_base64


def ocr_with_claude(image_base64, page_number):
    """
    Use Claude Vision API to OCR the image
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        # Try to load from .env file
        env_file = Path(__file__).parent / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("ANTHROPIC_API_KEY="):
                    api_key = line.split("=", 1)[1].strip().strip('"')
                    break

    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not found")
        print(
            "Please set ANTHROPIC_API_KEY environment variable or add it to .env file"
        )
        print("\nYou can:")
        print("  1. export ANTHROPIC_API_KEY='your-key-here'")
        print("  2. Add 'ANTHROPIC_API_KEY=your-key-here' to .env file")
        sys.exit(1)

    client = Anthropic(api_key=api_key)

    prompt = f"""You are OCRing page {page_number} from Whitney's Sanskrit Grammar (7th Edition, 1931).

This page contains Sanskrit grammar rules with:
- Rule numbers (§ 7, § 8, § 9, § 10, etc.)
- Rule titles in English
- Explanations mixing English with Sanskrit terms
- Sanskrit text in Devanagari script
- IAST transliteration of Sanskrit terms
- Examples with both Devanagari and romanized forms
- Footnotes with references

Please extract ALL text from this image with extreme accuracy.

CRITICAL REQUIREMENTS:
1. Preserve exact formatting and paragraph structure
2. For Devanagari text, transcribe it exactly as you see it
3. For romanized Sanskrit (IAST), preserve all diacritical marks (ā, ī, ū, ṛ, ṃ, ḥ, ś, ṣ, ñ, etc.)
4. Keep footnote markers and footnote text
5. Maintain any special formatting (italics, bold, etc.)
6. Note any unclear or uncertain text with [?]

Output the complete OCR text, preserving all formatting and special characters."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_base64,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    )

    return message.content[0].text


def main():
    # Try different PDFs in order of preference
    pdf_candidates = [
        "source/candidates/DLI_2015_IGNCA_Delhi.pdf",
        "source/candidates/Official_7th_Edition_1931.pdf",
        "source/candidates/xMqc_1931_Mulgaokar.pdf",
    ]

    base_dir = Path("/Users/skmnktl/Downloads/ocr")
    output_dir = base_dir / "source/missing_pages/ocr_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # PDF pages 24-25 (0-indexed: 23-24)
    pages_to_ocr = [23, 24]

    print("=" * 70)
    print("OCR MISSING PAGES 24-25")
    print("=" * 70)

    for pdf_rel_path in pdf_candidates:
        pdf_path = base_dir / pdf_rel_path
        if not pdf_path.exists():
            print(f"\n✗ PDF not found: {pdf_path}")
            continue

        print(f"\n\nUsing PDF: {pdf_rel_path}")
        print("-" * 70)

        for page_num in pages_to_ocr:
            pdf_page_num = page_num + 1  # Human-readable page number
            print(f"\n📄 Processing PDF page {pdf_page_num} (index {page_num})...")

            try:
                # Convert PDF page to base64 image
                print(f"   Converting to image...")
                image_base64 = pdf_page_to_base64(str(pdf_path), page_num)

                # OCR with Claude
                print(f"   OCRing with Claude Vision...")
                ocr_text = ocr_with_claude(image_base64, pdf_page_num)

                # Save output
                output_file = output_dir / f"page_{pdf_page_num:03d}_ocr.txt"
                output_file.write_text(ocr_text, encoding="utf-8")

                print(f"   ✓ Saved to: {output_file}")
                print(f"   Length: {len(ocr_text)} characters")

            except Exception as e:
                print(f"   ✗ Error: {e}")
                import traceback

                traceback.print_exc()
                continue

        # If we successfully processed pages, don't try other PDFs
        if all(
            (output_dir / f"page_{p + 1:03d}_ocr.txt").exists() for p in pages_to_ocr
        ):
            print("\n" + "=" * 70)
            print("SUCCESS! OCR completed for both pages")
            print("=" * 70)
            print(f"\nOutput files:")
            for p in pages_to_ocr:
                output_file = output_dir / f"page_{p + 1:03d}_ocr.txt"
                if output_file.exists():
                    print(f"  - {output_file}")
            return

    print("\n" + "=" * 70)
    print("FAILED: Could not OCR pages from any PDF")
    print("=" * 70)


if __name__ == "__main__":
    main()
