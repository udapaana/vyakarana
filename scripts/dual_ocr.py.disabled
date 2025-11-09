#!/usr/bin/env python3
"""Dual OCR: Run both Google Vision and Claude Vision on each page.

This gives us two independent OCR results that we can compare and merge
for maximum accuracy.
"""

import os
import sys
from pathlib import Path
from google_vision_ocr_simple import ocr_pdf_page as google_ocr_page
from claude_vision_ocr import ocr_pdf_page as claude_ocr_page
from load_env import load_env, check_api_keys


def dual_ocr_page(
    pdf_path: Path,
    page_number: int,
    google_output_dir: Path,
    claude_output_dir: Path,
    google_api_key: str,
    preprocess: bool = True
) -> dict:
    """Run both Google and Claude OCR on a single page.

    Args:
        pdf_path: Path to PDF
        page_number: Page to process
        google_output_dir: Where to save Google results
        claude_output_dir: Where to save Claude results
        google_api_key: Google API key
        preprocess: Whether to preprocess

    Returns:
        Dict with both results
    """
    print(f"\n{'='*70}")
    print(f"Page {page_number}: Dual OCR (Google + Claude)")
    print('='*70)

    results = {
        'page': page_number,
        'google': None,
        'claude': None,
        'errors': []
    }

    # Run Google Vision OCR
    print("\n[1/2] Google Vision OCR...")
    try:
        google_result = google_ocr_page(
            pdf_path, page_number, google_output_dir,
            google_api_key, preprocess
        )
        results['google'] = google_result
        print(f"  ✓ Google: {google_result['confidence']:.2%} confidence")
    except Exception as e:
        error_msg = f"Google OCR failed: {e}"
        print(f"  ✗ {error_msg}")
        results['errors'].append(error_msg)

    # Run Claude Vision OCR
    print("\n[2/2] Claude Vision OCR...")
    try:
        claude_result = claude_ocr_page(
            pdf_path, page_number, claude_output_dir, preprocess
        )
        results['claude'] = claude_result
        chars = len(claude_result['text'])
        tokens = claude_result['usage']['input_tokens'] + claude_result['usage']['output_tokens']
        print(f"  ✓ Claude: {chars} chars, {tokens} tokens")
    except Exception as e:
        error_msg = f"Claude OCR failed: {e}"
        print(f"  ✗ {error_msg}")
        results['errors'].append(error_msg)

    # Summary
    if results['google'] and results['claude']:
        print(f"\n  ✓✓ Both OCR engines successful!")
    elif results['google'] or results['claude']:
        print(f"\n  ⚠ Partial success (one engine failed)")
    else:
        print(f"\n  ✗✗ Both engines failed")

    return results


def batch_dual_ocr(
    pdf_path: Path,
    start_page: int,
    end_page: int,
    google_api_key: str
):
    """Run dual OCR on a range of pages.

    Args:
        pdf_path: Path to PDF
        start_page: First page (1-indexed)
        end_page: Last page (inclusive)
        google_api_key: Google API key
    """
    google_dir = Path(__file__).parent.parent / "ocr_output/google"
    claude_dir = Path(__file__).parent.parent / "ocr_output/claude"

    print("="*70)
    print(f"Dual OCR Batch: Pages {start_page}-{end_page}")
    print("="*70)

    all_results = []
    both_success = 0
    partial_success = 0
    both_failed = 0

    for page_num in range(start_page, end_page + 1):
        result = dual_ocr_page(
            pdf_path, page_num, google_dir, claude_dir,
            google_api_key, preprocess=True
        )
        all_results.append(result)

        if result['google'] and result['claude']:
            both_success += 1
        elif result['google'] or result['claude']:
            partial_success += 1
        else:
            both_failed += 1

    # Summary
    total = end_page - start_page + 1
    print("\n" + "="*70)
    print("Dual OCR Summary")
    print("="*70)
    print(f"Total pages: {total}")
    print(f"Both successful: {both_success} ({100*both_success/total:.1f}%)")
    print(f"Partial success: {partial_success} ({100*partial_success/total:.1f}%)")
    print(f"Both failed: {both_failed}")

    # Cost estimate
    google_cost = both_success * 1.50 / 1000  # $1.50 per 1000 pages
    # Claude cost: ~1900 input tokens + ~800 output tokens per page
    # Sonnet pricing: $3/million input, $15/million output
    claude_cost = both_success * ((1900 * 3 + 800 * 15) / 1_000_000)

    print(f"\nEstimated costs:")
    print(f"  Google Vision: ${google_cost:.3f}")
    print(f"  Claude Vision: ${claude_cost:.3f}")
    print(f"  Total: ${google_cost + claude_cost:.3f}")

    return all_results


def main():
    """Run dual OCR on specified page range."""
    import argparse

    parser = argparse.ArgumentParser(description='Dual OCR with Google + Claude')
    parser.add_argument('--start', type=int, default=1, help='Start page')
    parser.add_argument('--end', type=int, default=5, help='End page')

    args = parser.parse_args()

    # Load API keys
    load_env()
    status = check_api_keys()

    if not status['google']['set']:
        print("Error: Google API key not set")
        sys.exit(1)

    # Note: Claude uses ANTHROPIC_API_KEY from environment

    google_api_key = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    pdf_path = Path(__file__).parent.parent / "source/candidates/DLI_2015_IGNCA_Delhi.pdf"

    if not pdf_path.exists():
        print(f"Error: {pdf_path} not found")
        sys.exit(1)

    # Run dual OCR
    batch_dual_ocr(pdf_path, args.start, args.end, google_api_key)


if __name__ == "__main__":
    main()
