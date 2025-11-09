#!/usr/bin/env python3
"""
Batch Manual OCR Processor - Displays images for human transcription
This script helps organize the manual OCR workflow without using the API
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import subprocess


def show_image(image_path):
    """Display image using system viewer"""
    subprocess.run(["open", "-a", "Preview", str(image_path)])


def get_next_batch(start_page, batch_size=5):
    """Get the next batch of pages to process"""
    image_dir = Path("phase1_ocr/images/official_1931")
    output_dir = Path("phase1_ocr/sources/official_1931")

    batch = []
    for page_num in range(start_page, start_page + batch_size):
        image_path = image_dir / f"{page_num:03d}.png"
        txt_path = output_dir / f"{page_num:03d}.txt"
        json_path = output_dir / f"{page_num:03d}.json"

        if not image_path.exists():
            print(f"⚠️  Image not found: {image_path}")
            continue

        if txt_path.exists() and json_path.exists():
            print(f"⊘  Page {page_num} already processed")
            continue

        batch.append(
            {"page": page_num, "image": image_path, "txt": txt_path, "json": json_path}
        )

    return batch


def open_all_images_in_batch(batch):
    """Open all images in Preview for viewing"""
    print(f"\n📖 Opening {len(batch)} images in Preview...")
    for item in batch:
        print(f"   Page {item['page']}: {item['image'].name}")
        show_image(item["image"])


def create_batch_manifest(batch, output_file="current_batch.json"):
    """Save batch info for easy reference"""
    manifest = {
        "created": datetime.now().isoformat(),
        "pages": [item["page"] for item in batch],
        "items": [
            {
                "page": item["page"],
                "image": str(item["image"]),
                "txt_output": str(item["txt"]),
                "json_output": str(item["json"]),
            }
            for item in batch
        ],
    }

    with open(output_file, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\n✅ Manifest saved: {output_file}")
    return output_file


def print_page_template(page_num, internal_page=None):
    """Print template for manual entry"""
    print(f"\n{'=' * 60}")
    print(f"PAGE {page_num}")
    print(f"{'=' * 60}")

    if internal_page:
        print(f"Internal page: {internal_page}")

    print(f"\nFiles to create:")
    print(f"  - {page_num:03d}.txt")
    print(f"  - {page_num:03d}.json")
    print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python batch_manual_ocr.py START_PAGE [BATCH_SIZE]")
        print("Example: python batch_manual_ocr.py 251 5")
        sys.exit(1)

    start_page = int(sys.argv[1])
    batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    print(f"\n🔍 Preparing batch starting from page {start_page}")
    print(f"   Batch size: {batch_size}")

    batch = get_next_batch(start_page, batch_size)

    if not batch:
        print("\n✅ No pages to process!")
        return

    print(f"\n📋 Found {len(batch)} pages to process:")
    for item in batch:
        print(f"   • Page {item['page']}")

    # Create manifest
    manifest_file = create_batch_manifest(batch)

    # Open images
    response = input("\n🖼️  Open all images in Preview? (y/n): ")
    if response.lower() == "y":
        open_all_images_in_batch(batch)

    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("1. View the images opened in Preview")
    print("2. Copy the images to your clipboard or share with Claude Code")
    print("3. Ask Claude Code to transcribe them")
    print(f"4. Manifest saved in: {manifest_file}")
    print("\nOr simply tell Claude Code: 'Process the images from batch manifest'")
    print("=" * 60)


if __name__ == "__main__":
    main()
