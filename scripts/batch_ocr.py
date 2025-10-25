#!/usr/bin/env python3
"""Batch process multiple pages with Google Vision OCR.

This is the main OCR pipeline that processes pages in batches.
"""

import os
import sys
from pathlib import Path
from google_vision_ocr_simple import ocr_pdf_page
from load_env import load_env, check_api_keys


def batch_process_pages(
    pdf_path: Path,
    output_dir: Path,
    api_key: str,
    start_page: int = 1,
    end_page: int = 729,
    preprocess: bool = True
):
    """Process a range of pages with Google Vision OCR.

    Args:
        pdf_path: Path to source PDF
        output_dir: Where to save OCR results
        api_key: Google Cloud API key
        start_page: First page to process (1-indexed)
        end_page: Last page to process (inclusive)
        preprocess: Whether to preprocess images
    """
    print("="*70)
    print(f"Batch OCR: Pages {start_page}-{end_page}")
    print("="*70)
    print()

    successful = []
    failed = []

    for page_num in range(start_page, end_page + 1):
        try:
            print(f"\n[{page_num}/{end_page}]")
            result = ocr_pdf_page(
                pdf_path,
                page_num,
                output_dir,
                api_key,
                preprocess=preprocess
            )
            successful.append(page_num)

        except Exception as e:
            print(f"  ✗ Error on page {page_num}: {e}")
            failed.append(page_num)

            # Save error log
            error_log = output_dir / "errors.txt"
            with error_log.open('a') as f:
                f.write(f"Page {page_num}: {e}\n")

    # Summary
    print()
    print("="*70)
    print("Batch OCR Summary")
    print("="*70)
    print(f"Successful: {len(successful)}/{end_page - start_page + 1}")
    print(f"Failed: {len(failed)}")

    if failed:
        print(f"\nFailed pages: {failed}")
        print(f"See {output_dir}/errors.txt for details")

    return successful, failed


def main():
    """Run batch OCR on specified page range."""
    import argparse

    parser = argparse.ArgumentParser(description='Batch OCR with Google Vision')
    parser.add_argument('--start', type=int, default=1, help='Start page (default: 1)')
    parser.add_argument('--end', type=int, default=10, help='End page (default: 10)')
    parser.add_argument('--no-preprocess', action='store_true', help='Skip preprocessing')

    args = parser.parse_args()

    # Load API key
    load_env()
    status = check_api_keys()

    if not status['google']['set']:
        print("Error: Google API key not configured")
        print("Edit .env file and set GOOGLE_APPLICATION_CREDENTIALS")
        sys.exit(1)

    api_key = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

    # Set paths
    pdf_path = Path(__file__).parent.parent / "source/candidates/DLI_2015_IGNCA_Delhi.pdf"
    output_dir = Path(__file__).parent.parent / "ocr_output/google"

    if not pdf_path.exists():
        print(f"Error: {pdf_path} not found")
        sys.exit(1)

    # Run batch processing
    batch_process_pages(
        pdf_path,
        output_dir,
        api_key,
        start_page=args.start,
        end_page=args.end,
        preprocess=not args.no_preprocess
    )


if __name__ == "__main__":
    main()
