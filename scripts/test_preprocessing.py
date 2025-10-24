#!/usr/bin/env python3
"""Test preprocessing on sample pages and save before/after comparisons."""

from pathlib import Path
from pdf2image import convert_from_path
from preprocess_image import preprocess_for_ocr


def test_preprocessing(pdf_path: Path, page_num: int = 50):
    """Extract a page, apply preprocessing, and save comparison."""
    print(f"Testing preprocessing on page {page_num}...")

    # Extract page
    print("  Extracting page from PDF...")
    images = convert_from_path(pdf_path, first_page=page_num, last_page=page_num, dpi=300)

    if not images:
        print("  Error: Could not extract page")
        return

    original = images[0]

    # Create output directory
    output_dir = Path("preprocessing_test")
    output_dir.mkdir(exist_ok=True)

    # Save original
    original_path = output_dir / f"page_{page_num}_original.png"
    original.save(original_path)
    print(f"  Saved original: {original_path}")

    # Test different preprocessing settings
    configs = {
        "light": {
            "deskew": True,
            "contrast": 1.2,
            "sharpness": 1.1,
            "denoise": True,
            "remove_border": True,
            "binarize_mode": None
        },
        "medium": {
            "deskew": True,
            "contrast": 1.3,
            "sharpness": 1.2,
            "denoise": True,
            "remove_border": True,
            "binarize_mode": None
        },
        "heavy": {
            "deskew": True,
            "contrast": 1.5,
            "sharpness": 1.3,
            "denoise": True,
            "remove_border": True,
            "binarize_mode": None
        },
        "binarized": {
            "deskew": True,
            "contrast": 1.3,
            "sharpness": 1.2,
            "denoise": True,
            "remove_border": True,
            "binarize_mode": "adaptive"
        },
    }

    for name, config in configs.items():
        print(f"  Applying {name} preprocessing...")
        preprocessed = preprocess_for_ocr(original, **config)

        output_path = output_dir / f"page_{page_num}_{name}.png"
        preprocessed.save(output_path)
        print(f"    Saved: {output_path}")

    print()
    print(f"Results saved to {output_dir}/")
    print("Compare the images to see which preprocessing works best!")


def main():
    print("="*70)
    print("Preprocessing Test")
    print("="*70)
    print()

    # Use DLI source (winner from quality comparison)
    pdf_path = Path("source/candidates/DLI_2015_IGNCA_Delhi.pdf")

    if not pdf_path.exists():
        print(f"Error: {pdf_path} not found")
        return

    # Test on a page with substantial text (around page 50)
    test_preprocessing(pdf_path, page_num=50)

    print()
    print("Recommendations:")
    print("  - 'light': Good balance, preserves gray-scale details")
    print("  - 'medium': Recommended for most OCR (what we'll use)")
    print("  - 'heavy': If pages are very faded or low contrast")
    print("  - 'binarized': For some OCR engines that prefer pure B&W")


if __name__ == "__main__":
    main()
