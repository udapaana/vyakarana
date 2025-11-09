#!/usr/bin/env python3
"""OCR official_1931 source images using Claude Vision API.

Processes extracted PNG images from phase1_ocr/images/official_1931/
and saves OCR results to phase1_ocr/sources/official_1931/
"""

import argparse
from pathlib import Path
import sys

# Import our OCR module
sys.path.insert(0, str(Path(__file__).parent))
from claude_vision_ocr import ocr_image_with_claude
from PIL import Image


def process_official_1931_images(start: int, end: int, skip_existing: bool = True):
    """Process official_1931 images with Claude OCR."""

    image_dir = Path("phase1_ocr/images/official_1931")
    output_dir = Path("phase1_ocr/sources/official_1931")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("OCR Official_1931 Source with Claude Vision")
    print("=" * 70)
    print(f"Pages: {start}-{end}")
    print(f"Input: {image_dir}/")
    print(f"Output: {output_dir}/")
    print()

    processed = 0
    skipped = 0
    errors = 0

    for page_num in range(start, end + 1):
        page_name = f"page_{page_num:03d}"
        image_path = image_dir / f"{page_name}.png"
        txt_path = output_dir / f"{page_name}.txt"
        json_path = output_dir / f"{page_name}.json"

        # Skip if image doesn't exist yet
        if not image_path.exists():
            continue

        # Skip if already processed
        if skip_existing and txt_path.exists() and json_path.exists():
            skipped += 1
            print(f"Page {page_num}: ✓ cached")
            continue

        # Process with Claude
        try:
            print(f"Page {page_num}: ", end="", flush=True)

            # Load image
            image = Image.open(image_path)

            # OCR
            result = ocr_image_with_claude(image)

            # Save results
            txt_path.write_text(result["text"])

            import json

            with json_path.open("w") as f:
                json.dump(result, f, indent=2)

            print(
                f"✓ {len(result['text'])} chars, "
                f"{result['usage']['input_tokens']}+{result['usage']['output_tokens']} tokens"
            )

            processed += 1

        except Exception as e:
            print(f"✗ Error: {e}")
            errors += 1

    # Summary
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Processed: {processed}")
    print(f"Skipped (cached): {skipped}")
    print(f"Errors: {errors}")
    print()
    print(f"Output: {output_dir}/page_*.{{txt,json}}")


def main():
    parser = argparse.ArgumentParser(description="OCR official_1931 source images")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=732)
    parser.add_argument(
        "--no-skip", action="store_true", help="Reprocess existing pages"
    )

    args = parser.parse_args()

    process_official_1931_images(args.start, args.end, skip_existing=not args.no_skip)


if __name__ == "__main__":
    main()
