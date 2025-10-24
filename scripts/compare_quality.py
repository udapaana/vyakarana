#!/usr/bin/env python3
"""Compare image quality between multiple 7th edition scans.

For each page, select the scan with better quality based on:
- Sharpness (Laplacian variance)
- Resolution
- Contrast

Following coding standards:
- Deep module: User specifies page range, gets best source selection
- Comments explain why: Why certain metrics matter for OCR accuracy
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pdf2image import convert_from_path
from PIL import Image, ImageStat, ImageFilter


@dataclass
class PageQuality:
    """Quality metrics for a single page from a source."""
    source_name: str
    page_number: int
    resolution: tuple[int, int]  # (width, height)
    sharpness: float  # Laplacian variance
    contrast: float   # Standard deviation
    brightness: float # Mean pixel value

    def score(self) -> float:
        """Calculate overall quality score.

        Why this formula: OCR accuracy correlates strongly with sharpness
        and resolution. Contrast helps but is secondary.
        """
        # Normalize resolution (typical page ~2000x3000 pixels)
        res_score = (self.resolution[0] * self.resolution[1]) / (2000 * 3000)
        res_score = min(res_score, 1.5)  # Cap at 1.5x typical

        # Sharpness is most critical for OCR
        sharp_score = min(self.sharpness / 1000.0, 1.0)

        # Contrast helps distinguish text from background
        contrast_score = min(self.contrast / 100.0, 1.0)

        # Weighted: 50% sharpness, 30% resolution, 20% contrast
        return 0.5 * sharp_score + 0.3 * res_score + 0.2 * contrast_score


def calculate_sharpness(image: Image.Image) -> float:
    """Calculate sharpness using Laplacian variance.

    Why Laplacian: Measures edge definition, critical for OCR.
    Higher variance = sharper edges = clearer text.
    """
    gray = image.convert('L')

    # Apply Laplacian filter
    laplacian = gray.filter(ImageFilter.Kernel(
        size=(3, 3),
        kernel=[-1, -1, -1, -1, 8, -1, -1, -1, -1],
        scale=1
    ))

    return ImageStat.Stat(laplacian).var[0]


def analyze_page(image: Image.Image, source_name: str, page_num: int) -> PageQuality:
    """Analyze quality metrics for a page image."""
    gray = image.convert('L')
    stat = ImageStat.Stat(gray)

    return PageQuality(
        source_name=source_name,
        page_number=page_num,
        resolution=image.size,
        sharpness=calculate_sharpness(image),
        contrast=stat.stddev[0],
        brightness=stat.mean[0]
    )


def extract_and_compare_page(
    sources: Dict[str, Path],
    page_number: int,
    dpi: int = 300
) -> Dict[str, PageQuality]:
    """Extract and analyze a page from each source.

    Args:
        sources: Dict mapping source names to PDF paths
        page_number: Page to extract (1-indexed)
        dpi: Resolution for extraction

    Returns:
        Dict mapping source names to their PageQuality
    """
    results = {}

    for source_name, pdf_path in sources.items():
        try:
            # Extract single page
            images = convert_from_path(
                pdf_path,
                first_page=page_number,
                last_page=page_number,
                dpi=dpi
            )

            if images:
                quality = analyze_page(images[0], source_name, page_number)
                results[source_name] = quality

        except Exception as e:
            print(f"  Warning: Failed to process {source_name} page {page_number}: {e}")

    return results


def compare_all_pages(
    sources: Dict[str, Path],
    start_page: int = 1,
    end_page: Optional[int] = None,
    output_json: Path = Path("quality_comparison.json")
) -> Dict[int, str]:
    """Compare all pages and select best source for each.

    Args:
        sources: Dict mapping source names to PDF paths
        start_page: First page to compare
        end_page: Last page to compare (None = all pages)
        output_json: Where to save detailed results

    Returns:
        Dict mapping page numbers to best source name
    """
    # Determine page range
    if end_page is None:
        # Use minimum page count across sources
        from PyPDF2 import PdfReader
        end_page = min(len(PdfReader(pdf).pages) for pdf in sources.values())

    print(f"Comparing pages {start_page}-{end_page} across {len(sources)} sources...")
    print()

    best_sources = {}
    detailed_results = {}

    for page_num in range(start_page, end_page + 1):
        print(f"Page {page_num}/{end_page}...", end=" ")

        # Compare this page across all sources
        page_results = extract_and_compare_page(sources, page_num)

        if not page_results:
            print("SKIP (no sources)")
            continue

        # Find best source for this page
        best_source = max(page_results.items(), key=lambda x: x[1].score())
        best_sources[page_num] = best_source[0]
        detailed_results[page_num] = {
            name: asdict(quality)
            for name, quality in page_results.items()
        }

        # Show winner
        scores_str = ", ".join(
            f"{name}: {q.score():.3f}"
            for name, q in page_results.items()
        )
        print(f"→ {best_source[0]} ({scores_str})")

    # Save detailed results
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with output_json.open('w') as f:
        json.dump({
            "best_sources": best_sources,
            "detailed_metrics": detailed_results
        }, f, indent=2)

    print(f"\nResults saved to {output_json}")

    # Print summary
    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    source_counts = {}
    for source in best_sources.values():
        source_counts[source] = source_counts.get(source, 0) + 1

    for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
        pct = 100 * count / len(best_sources)
        print(f"{source}: {count} pages ({pct:.1f}%)")

    return best_sources


def main():
    """Compare quality between verified 7th edition sources."""
    print("="*70)
    print("7th Edition Quality Comparison")
    print("="*70)
    print()

    # Load verified sources
    sources = {
        "Official_1931": Path("source/candidates/Official_7th_Edition_1931.pdf"),
        "DLI_2015": Path("source/candidates/DLI_2015_IGNCA_Delhi.pdf"),
    }

    # Verify all sources exist
    for name, path in sources.items():
        if not path.exists():
            print(f"Error: {path} not found")
            print("Run download_7th_edition_sources.py first")
            return
        print(f"Found: {name} ({path})")

    print()
    print("Comparing first 10 pages as test...")
    print("(Edit script to compare all pages)")
    print()

    # Compare first 10 pages as test
    best_sources = compare_all_pages(
        sources,
        start_page=1,
        end_page=10,
        output_json=Path("quality_comparison.json")
    )

    print("\nNext steps:")
    print("  1. Review quality_comparison.json")
    print("  2. Run select_best_images.py to extract best pages")
    print("  3. Proceed with OCR pipeline")


if __name__ == "__main__":
    main()
