#!/usr/bin/env python3
"""
OCR script for PDFs - outputs one raw text file per page.
Simplified: Just does OCR, no chapter detection.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image, ImageEnhance, ImageFilter
except ImportError as e:
    print(f"Error: Missing required package: {e}", file=sys.stderr)
    print("Please run: uv sync", file=sys.stderr)
    sys.exit(1)


def preprocess_image(image: Image.Image, enhance: bool = True) -> Image.Image:
    """
    Preprocess image for better OCR accuracy.

    Args:
        image: PIL Image object
        enhance: Whether to apply enhancement

    Returns:
        Preprocessed PIL Image
    """
    if not enhance:
        return image

    # Convert to grayscale
    if image.mode != 'L':
        image = image.convert('L')

    # Increase contrast (helps with faded text)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.5)

    # Sharpen (helps with diacritics)
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(1.3)

    # Denoise (remove scan artifacts)
    image = image.filter(ImageFilter.MedianFilter(size=3))

    return image


def ocr_page(
    pdf_path: str,
    page_num: int,
    output_dir: Path,
    languages: str = "eng+san",
    dpi: int = 300,
    preprocess: bool = True,
    quiet: bool = False,
) -> str:
    """
    OCR a single page and save to file.

    Args:
        pdf_path: Path to PDF
        page_num: Page number (1-indexed)
        output_dir: Output directory
        languages: Tesseract languages
        dpi: DPI for conversion
        preprocess: Whether to preprocess
        quiet: Suppress messages

    Returns:
        Path to output file
    """
    def log(msg):
        if not quiet:
            print(msg, file=sys.stderr)

    # Convert single page
    images = convert_from_path(
        pdf_path,
        dpi=dpi,
        first_page=page_num,
        last_page=page_num,
    )

    if not images:
        raise ValueError(f"Could not convert page {page_num}")

    image = images[0]

    # Preprocess
    if preprocess:
        image = preprocess_image(image, enhance=True)

    # OCR
    text = pytesseract.image_to_string(
        image,
        lang=languages,
        config='--psm 6'
    )

    # Save raw page text
    output_file = output_dir / f"page_{page_num:04d}.txt"
    output_file.write_text(text, encoding='utf-8')

    log(f"✓ Page {page_num} → {output_file.name}")

    return str(output_file)


def ocr_pdf(
    pdf_path: str,
    output_dir: Optional[str] = None,
    languages: str = "eng+san",
    dpi: int = 300,
    first_page: Optional[int] = None,
    last_page: Optional[int] = None,
    preprocess: bool = True,
    quiet: bool = False,
):
    """
    OCR PDF pages individually.
    """
    pdf_file = Path(pdf_path)

    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    def log(msg):
        if not quiet:
            print(msg, file=sys.stderr)

    # Setup output directory
    if output_dir:
        out_dir = Path(output_dir)
    else:
        out_dir = Path("raw_pages")

    out_dir.mkdir(exist_ok=True)

    # Determine page range
    if not last_page:
        # Get total pages
        from pdf2image import pdfinfo_from_path
        info = pdfinfo_from_path(pdf_path)
        total_pages = info.get('Pages', 0)
        last_page = total_pages

    if not first_page:
        first_page = 1

    log(f"OCR PDF: {pdf_file.name}")
    log(f"Output: {out_dir}/")
    log(f"Pages: {first_page}-{last_page}")
    log(f"DPI: {dpi}")
    log(f"Languages: {languages}")
    log(f"Preprocessing: {'enabled' if preprocess else 'disabled'}")
    log("-" * 60)

    # Process each page
    processed = 0
    failed = 0

    for page_num in range(first_page, last_page + 1):
        try:
            # Check if already processed
            output_file = out_dir / f"page_{page_num:04d}.txt"
            if output_file.exists():
                log(f"⊙ Page {page_num} (already exists, skipping)")
                processed += 1
                continue

            ocr_page(
                pdf_path=pdf_path,
                page_num=page_num,
                output_dir=out_dir,
                languages=languages,
                dpi=dpi,
                preprocess=preprocess,
                quiet=quiet,
            )
            processed += 1

        except Exception as e:
            log(f"✗ Page {page_num} failed: {e}")
            failed += 1

    log("-" * 60)
    log(f"✓ Processed: {processed}/{last_page - first_page + 1}")
    if failed > 0:
        log(f"✗ Failed: {failed}")

    log(f"\nNext steps:")
    log(f"  1. Aggregate pages into chapters: python aggregate_chapters.py")
    log(f"  2. Clean with Claude: ./cleanup_chapters.sh")


def main():
    parser = argparse.ArgumentParser(
        description="OCR PDF pages individually - one text file per page",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # OCR entire PDF
  python ocr_pages.py input.pdf

  # OCR specific pages
  python ocr_pages.py input.pdf --first-page 1 --last-page 50

  # Higher quality
  python ocr_pages.py input.pdf --dpi 600

  # Resume from page 100
  python ocr_pages.py input.pdf --first-page 100
  (Already processed pages are automatically skipped)
        """
    )

    parser.add_argument(
        "pdf_path",
        help="Path to the PDF file to OCR"
    )

    parser.add_argument(
        "-o", "--output-dir",
        help="Directory to save page text files (default: raw_pages/)"
    )

    parser.add_argument(
        "-l", "--languages",
        default="eng+san",
        help="Tesseract language codes (default: eng+san)"
    )

    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="DPI for PDF conversion (default: 300)"
    )

    parser.add_argument(
        "--first-page",
        type=int,
        help="First page to process (1-indexed)"
    )

    parser.add_argument(
        "--last-page",
        type=int,
        help="Last page to process (1-indexed)"
    )

    parser.add_argument(
        "--no-preprocess",
        action="store_true",
        help="Disable image preprocessing"
    )

    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress progress messages"
    )

    args = parser.parse_args()

    try:
        ocr_pdf(
            pdf_path=args.pdf_path,
            output_dir=args.output_dir,
            languages=args.languages,
            dpi=args.dpi,
            first_page=args.first_page,
            last_page=args.last_page,
            preprocess=not args.no_preprocess,
            quiet=args.quiet,
        )

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
