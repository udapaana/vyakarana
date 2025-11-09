#!/usr/bin/env python3
"""Build page-to-page equivalency mapping across multiple sources.

Why we need this: Different scans may have different page counts due to:
- Different front matter
- Blank pages included/excluded
- Scanning artifacts

This script creates a mapping between canonical page numbers and actual page
numbers in each source by:
1. Extracting sample text from each page
2. Computing similarity between pages across sources
3. Building equivalency map

Following coding standards:
- Deep module: User runs once, gets complete mapping
- Comments explain why: Why content-based matching is needed
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from difflib import SequenceMatcher


@dataclass
class PageFingerprint:
    """Quick fingerprint of a page for matching."""

    source: str
    page_num: int
    text_sample: str  # First ~500 chars
    char_count: int
    has_devanagari: bool
    has_latin: bool

    def similarity(self, other: "PageFingerprint") -> float:
        """Calculate similarity score with another page.

        Why this metric: Combines text similarity with structural features.
        Same page should have >0.8 similarity even with OCR differences.
        """
        # Text similarity (main signal)
        text_sim = SequenceMatcher(None, self.text_sample, other.text_sample).ratio()

        # Character count similarity (pages should be similar length)
        if self.char_count == 0 and other.char_count == 0:
            count_sim = 1.0
        elif self.char_count == 0 or other.char_count == 0:
            count_sim = 0.0
        else:
            count_sim = min(self.char_count, other.char_count) / max(
                self.char_count, other.char_count
            )

        # Script similarity (same script mix)
        script_sim = (
            1.0
            if (
                self.has_devanagari == other.has_devanagari
                and self.has_latin == other.has_latin
            )
            else 0.5
        )

        # Weighted combination: 70% text, 20% length, 10% script
        return 0.7 * text_sim + 0.2 * count_sim + 0.1 * script_sim


def extract_page_fingerprint(
    pdf_path: Path, page_num: int, source_name: str, dpi: int = 150
) -> Optional[PageFingerprint]:
    """Extract a quick fingerprint from a PDF page.

    Why low DPI: We only need rough text for matching, not perfect OCR.
    150 DPI is 5x faster than 300 and sufficient for page matching.

    Args:
        pdf_path: Path to PDF
        page_num: Page number (1-indexed)
        source_name: Name of source
        dpi: Resolution for extraction

    Returns:
        PageFingerprint or None if failed
    """
    try:
        # Extract page as image
        images = convert_from_path(
            pdf_path, first_page=page_num, last_page=page_num, dpi=dpi
        )

        if not images:
            return None

        # Quick OCR with Tesseract (much faster than Claude for matching)
        text = pytesseract.image_to_string(
            images[0],
            lang="san+eng",  # Sanskrit + English
            config="--psm 6",  # Assume uniform text block
        )

        # Extract features
        text_sample = text[:500].strip()
        char_count = len(text.strip())

        # Detect scripts (rough heuristic)
        has_devanagari = any("\u0900" <= c <= "\u097f" for c in text)
        has_latin = any("a" <= c.lower() <= "z" for c in text)

        return PageFingerprint(
            source=source_name,
            page_num=page_num,
            text_sample=text_sample,
            char_count=char_count,
            has_devanagari=has_devanagari,
            has_latin=has_latin,
        )

    except Exception as e:
        print(f"    Error extracting page {page_num}: {e}")
        return None


def find_matching_page(
    canonical_fp: PageFingerprint,
    source_pages: List[PageFingerprint],
    min_similarity: float = 0.7,
) -> Optional[Tuple[int, float]]:
    """Find the matching page in a source.

    Why minimum similarity: Avoid false matches from blank/title pages.
    0.7 threshold allows for OCR differences while rejecting mismatches.

    Args:
        canonical_fp: Fingerprint of canonical page
        source_pages: Fingerprints from source to search
        min_similarity: Minimum similarity threshold

    Returns:
        (page_number, similarity_score) or None if no match
    """
    best_match = None
    best_score = min_similarity

    for fp in source_pages:
        score = canonical_fp.similarity(fp)
        if score > best_score:
            best_score = score
            best_match = fp.page_num

    return (best_match, best_score) if best_match else None


def build_mapping(
    sources: Dict[str, Path],
    canonical_source: str,
    canonical_pages: range,
    sample_rate: int = 1,
) -> Dict[int, Dict[str, int]]:
    """Build page equivalency mapping across sources.

    Args:
        sources: Dict mapping source names to PDF paths
        canonical_source: Name of canonical/reference source
        canonical_pages: Range of canonical page numbers to map
        sample_rate: Process every Nth page (1 = all pages)

    Returns:
        Dict mapping canonical page nums to {source: actual_page_num}
    """
    print("=" * 70)
    print("Building Page Equivalency Mapping")
    print("=" * 70)
    print()
    print(f"Canonical source: {canonical_source}")
    print(f"Pages to map: {canonical_pages.start} to {canonical_pages.stop - 1}")
    print(f"Sample rate: Every {sample_rate} page(s)")
    print()

    # Step 1: Extract fingerprints from all sources
    print("Step 1: Extracting page fingerprints...")
    print()

    all_fingerprints = {}

    for source_name, pdf_path in sources.items():
        print(f"  {source_name}:")

        # Determine page range
        from PyPDF2 import PdfReader

        total_pages = len(PdfReader(pdf_path).pages)

        # For canonical source: use specified range
        # For others: scan all pages to find matches
        if source_name == canonical_source:
            pages_to_scan = list(canonical_pages)[::sample_rate]
        else:
            pages_to_scan = list(range(1, total_pages + 1))[::sample_rate]

        fingerprints = []
        for page_num in pages_to_scan:
            if page_num % 10 == 0:
                print(f"    Page {page_num}/{pages_to_scan[-1]}...", end="\r")

            fp = extract_page_fingerprint(pdf_path, page_num, source_name)
            if fp:
                fingerprints.append(fp)

        all_fingerprints[source_name] = fingerprints
        print(f"    Extracted {len(fingerprints)} fingerprints" + " " * 20)

    print()

    # Step 2: Build mapping
    print("Step 2: Matching pages across sources...")
    print()

    mapping = {}
    canonical_fps = all_fingerprints[canonical_source]

    for canonical_fp in canonical_fps:
        canonical_page = canonical_fp.page_num
        mapping[canonical_page] = {canonical_source: canonical_page}

        print(f"  Canonical page {canonical_page}:")

        # Find matches in other sources
        for source_name in sources:
            if source_name == canonical_source:
                continue

            match = find_matching_page(canonical_fp, all_fingerprints[source_name])

            if match:
                page_num, score = match
                mapping[canonical_page][source_name] = page_num
                print(f"    → {source_name}: page {page_num} (similarity: {score:.3f})")
            else:
                print(f"    → {source_name}: no match")

    print()
    return mapping


def main():
    """Build page equivalency mapping."""
    parser = argparse.ArgumentParser(
        description="Build page-to-page equivalency mapping across sources"
    )
    parser.add_argument(
        "--start", type=int, default=1, help="Start page (canonical numbering)"
    )
    parser.add_argument(
        "--end", type=int, default=50, help="End page (canonical numbering)"
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=1,
        help="Sample every Nth page (default: 1 = all pages)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/sources.json"),
        help="Source configuration file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("config/page_equivalency.json"),
        help="Output mapping file",
    )

    args = parser.parse_args()

    # Load source config
    with args.config.open() as f:
        config = json.load(f)

    sources = {
        name: Path(data["path"])
        for name, data in config["sources"].items()
        if data.get("verified", False)
    }

    canonical_source = config["page_mapping"]["canonical_source"]

    # Verify sources exist
    for name, path in sources.items():
        if not path.exists():
            print(f"Error: {path} not found")
            return 1

    # Build mapping
    mapping = build_mapping(
        sources, canonical_source, range(args.start, args.end + 1), args.sample
    )

    # Load existing mapping if exists
    if args.output.exists():
        with args.output.open() as f:
            existing = json.load(f)
    else:
        existing = {
            "mapping_version": "1.0",
            "canonical_source": canonical_source,
            "generated_date": None,
            "notes": "Page-to-page equivalency across all sources",
            "mappings": {},
            "unmapped": {},
            "statistics": {},
        }

    # Update with new mappings
    for page, sources_map in mapping.items():
        existing["mappings"][str(page)] = sources_map

    existing["generated_date"] = str(Path(__file__).stat().st_mtime)

    # Calculate statistics
    total_canonical = len(mapping)
    sources_per_page = {}
    for page_map in mapping.values():
        count = len(page_map)
        sources_per_page[count] = sources_per_page.get(count, 0) + 1

    existing["statistics"] = {
        "total_canonical_pages": total_canonical,
        "mapped_pages": total_canonical,
        "sources_per_page": sources_per_page,
    }

    # Save
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as f:
        json.dump(existing, f, indent=2)

    print("=" * 70)
    print("Mapping Complete")
    print("=" * 70)
    print(f"Output: {args.output}")
    print(f"Mapped pages: {total_canonical}")
    print()
    print("Coverage per page:")
    for count in sorted(sources_per_page.keys(), reverse=True):
        pct = 100 * sources_per_page[count] / total_canonical
        print(f"  {count} sources: {sources_per_page[count]} pages ({pct:.1f}%)")
    print()
    print("Next step: Run multi_source_ocr.py with this mapping")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
