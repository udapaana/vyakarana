#!/usr/bin/env python3
"""
OCR the correct pages (24-25) containing § 7-10
"""

import os
import sys
import base64
import json
from pathlib import Path
from anthropic import Anthropic
import fitz  # PyMuPDF


def pdf_page_to_base64(pdf_path, page_number):
    """Extract a page from PDF and convert to base64 image"""
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


def ocr_with_claude(image_base64, page_number, section_info):
    """Use Claude Vision API to OCR the image"""
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
        sys.exit(1)

    client = Anthropic(api_key=api_key)

    prompt = f"""You are OCRing page {page_number} from Whitney's Sanskrit Grammar (7th Edition, 1931).

This page contains: {section_info}

Please extract ALL text from this image with EXTREME accuracy.

CRITICAL REQUIREMENTS:
1. Preserve exact formatting, paragraph structure, and section numbers
2. For Devanagari text, transcribe it EXACTLY as shown
3. For romanized Sanskrit (IAST), preserve ALL diacritical marks:
   - ā, ī, ū, ṛ, ṝ, ḷ (vowels with macron)
   - ṃ (anusvāra), ḥ (visarga)
   - ś, ṣ (palatals/retroflexes)
   - ṭ, ḍ, ṇ (retroflexes)
   - ñ (palatal nasal)
4. Keep footnote markers (superscripts) and footnote text
5. Maintain paragraph breaks and indentation
6. Note section headers like "§ 7.", "§ 8." etc.
7. Mark any unclear text with [?]

Output the complete OCR text exactly as it appears on the page."""

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
    base_dir = Path("/Users/skmnktl/Downloads/ocr")
    pdf_path = base_dir / "source/missing_pages/pages_024-025_rules_7-10.pdf"
    output_dir = base_dir / "source/missing_pages/ocr_correct"
    output_dir.mkdir(parents=True, exist_ok=True)

    pages_info = [
        (0, 24, "§ 7-8 - Consonant classification (Alpa-prāṇa and Mahā-prāṇa)"),
        (1, 25, "§ 9-10 - Consonant groups and pronunciation"),
    ]

    print("=" * 70)
    print("OCR CORRECT PAGES FOR § 7-10")
    print("=" * 70)

    for page_idx, pdf_page_num, section_info in pages_info:
        print(
            f"\n📄 Processing PDF page {pdf_page_num} (§ {7 + page_idx * 2}-{8 + page_idx * 2})..."
        )
        print(f"   Section: {section_info}")

        try:
            # Convert PDF page to base64 image
            print(f"   Converting to image...")
            image_base64 = pdf_page_to_base64(str(pdf_path), page_idx)

            # OCR with Claude
            print(f"   OCRing with Claude Vision...")
            ocr_text = ocr_with_claude(image_base64, pdf_page_num, section_info)

            # Save output
            output_file = (
                output_dir
                / f"page_{pdf_page_num:03d}_sections_{7 + page_idx * 2}-{8 + page_idx * 2}.txt"
            )
            output_file.write_text(ocr_text, encoding="utf-8")

            print(f"   ✓ Saved to: {output_file}")
            print(f"   Length: {len(ocr_text)} characters")

        except Exception as e:
            print(f"   ✗ Error: {e}")
            import traceback

            traceback.print_exc()
            continue

    print("\n" + "=" * 70)
    print("OCR COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
