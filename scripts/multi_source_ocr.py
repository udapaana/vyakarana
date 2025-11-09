#!/usr/bin/env python3
"""Multi-source OCR using Claude Vision across multiple PDF scans.

This script processes the SAME content from multiple source PDFs to:
1. Compensate for image quality deficiencies in any single source
2. Build page-to-page equivalency mapping across sources
3. Run Claude OCR on all sources for collective processing

DOES NOT replace existing dual_ocr.py or phase1_ocr outputs.
Creates new directory structure: phase1_ocr/sources/{source_name}/

Following coding standards:
- Deep module: Simple interface, complex implementation
- Comments explain why: Why we need multiple sources of same content
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import sys

# Import existing modules
from preprocess_image import preprocess_for_ocr
from claude_vision_ocr import ocr_pdf_page


@dataclass
class SourceConfig:
    """Configuration for a single PDF source."""

    name: str
    path: Path
    total_pages: int
    priority: int
    verified: bool
    page_offset: int = 0

    @classmethod
    def from_dict(cls, name: str, data: dict):
        """Load from config JSON."""
        return cls(
            name=name,
            path=Path(data["path"]),
            total_pages=data["total_pages"],
            priority=data["priority"],
            verified=data["verified"],
            page_offset=data.get("page_offset", 0),
        )


def load_source_config(
    config_path: Path = Path("config/sources.json"),
) -> Dict[str, SourceConfig]:
    """Load source configurations from JSON file.

    Why separate config: Allows adding/removing sources without code changes.
    """
    with config_path.open() as f:
        data = json.load(f)

    sources = {}
    for name, source_data in data["sources"].items():
        if source_data.get("verified", False):  # Only load verified sources
            sources[name] = SourceConfig.from_dict(name, source_data)

    return sources


def get_output_paths(
    base_dir: Path, source_name: str, page_num: int
) -> Tuple[Path, Path, Path]:
    """Get output paths for a source page.

    Structure: phase1_ocr/sources/{source_name}/page_{num:03d}.{txt,json,png}

    Why this structure: Keep multi-source OCR separate from original dual OCR.
    """
    source_dir = base_dir / "sources" / source_name
    source_dir.mkdir(parents=True, exist_ok=True)

    page_base = f"page_{page_num:03d}"
    return (
        source_dir / f"{page_base}.txt",
        source_dir / f"{page_base}.json",
        source_dir / f"{page_base}.png",
    )


def process_page(
    source: SourceConfig, page_num: int, output_dir: Path, skip_existing: bool = True
) -> Optional[dict]:
    """Process a single page from a source with Claude OCR.

    Args:
        source: Source configuration
        page_num: Page number to process (1-indexed)
        output_dir: Base output directory (e.g., phase1_ocr)
        skip_existing: Skip if output already exists

    Returns:
        OCR result dict or None if skipped/failed
    """
    txt_path, json_path, png_path = get_output_paths(output_dir, source.name, page_num)

    # Skip if exists
    if skip_existing and txt_path.exists() and json_path.exists():
        print(f"  ✓ {source.name} page {page_num} (cached)")
        return None

    # Check page is within bounds
    if page_num > source.total_pages:
        print(
            f"  ✗ {source.name} page {page_num} (out of range, max={source.total_pages})"
        )
        return None

    try:
        # Run Claude OCR (uses existing claude_vision_ocr.py)
        print(f"  → {source.name} page {page_num}...", end=" ", flush=True)

        result = ocr_pdf_page(
            pdf_path=str(source.path),
            page_number=page_num,
            output_dir=str(output_dir / "sources" / source.name),
        )

        # Save results
        txt_path.write_text(result["text"])
        json_path.write_text(json.dumps(result, indent=2))

        print(
            f"✓ ({result['usage']['input_tokens']}+{result['usage']['output_tokens']} tokens)"
        )

        return result

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def process_page_across_sources(
    sources: Dict[str, SourceConfig],
    canonical_page: int,
    output_dir: Path,
    page_mapping: Optional[Dict] = None,
) -> Dict[str, dict]:
    """Process a canonical page number across all available sources.

    Why across sources: Same content, multiple scans compensates for deficiencies.

    Args:
        sources: All available sources
        canonical_page: Canonical page number (from primary source)
        output_dir: Output directory
        page_mapping: Optional page equivalency mapping

    Returns:
        Dict mapping source names to their OCR results
    """
    print(f"\nCanonical page {canonical_page}:")
    results = {}

    for source_name, source in sorted(sources.items(), key=lambda x: x[1].priority):
        # Determine actual page number in this source
        if page_mapping and str(canonical_page) in page_mapping:
            actual_page = page_mapping[str(canonical_page)].get(source_name)
            if actual_page is None:
                print(f"  - {source_name}: No mapping")
                continue
        else:
            # Default: assume same page number
            actual_page = canonical_page

        result = process_page(source, actual_page, output_dir)
        if result:
            results[source_name] = result

    return results


def main():
    """Multi-source OCR with Claude Vision."""
    parser = argparse.ArgumentParser(
        description="Run Claude OCR on multiple sources of same content"
    )
    parser.add_argument(
        "--start", type=int, default=1, help="Start page (canonical numbering)"
    )
    parser.add_argument(
        "--end", type=int, required=True, help="End page (canonical numbering)"
    )
    parser.add_argument(
        "--pages", type=str, help="Specific pages (comma-separated, e.g., '1,5,10')"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("phase1_ocr"),
        help="Output directory (default: phase1_ocr)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/sources.json"),
        help="Source configuration file",
    )
    parser.add_argument(
        "--mapping",
        type=Path,
        default=Path("config/page_equivalency.json"),
        help="Page equivalency mapping file",
    )
    parser.add_argument(
        "--no-skip", action="store_true", help="Reprocess existing pages"
    )

    args = parser.parse_args()

    # Load configurations
    print("=" * 70)
    print("Multi-Source OCR with Claude Vision")
    print("=" * 70)
    print()

    # Load sources
    if not args.config.exists():
        print(f"Error: Config file not found: {args.config}")
        print("Run with default config or create config/sources.json")
        return 1

    sources = load_source_config(args.config)
    print(f"Loaded {len(sources)} verified sources:")
    for name, source in sorted(sources.items(), key=lambda x: x[1].priority):
        status = "✓" if source.path.exists() else "✗"
        print(
            f"  {status} {source.name}: {source.total_pages} pages (priority {source.priority})"
        )
    print()

    # Verify sources exist
    missing = [name for name, s in sources.items() if not s.path.exists()]
    if missing:
        print(f"Error: Missing source PDFs: {', '.join(missing)}")
        return 1

    # Load page mapping if exists
    page_mapping = None
    if args.mapping.exists():
        with args.mapping.open() as f:
            mapping_data = json.load(f)
            page_mapping = mapping_data.get("mappings", {})
        print(f"Loaded page equivalency mapping ({len(page_mapping)} pages mapped)")
    else:
        print("No page mapping found, using default 1:1 page numbers")
    print()

    # Determine pages to process
    if args.pages:
        pages = [int(p.strip()) for p in args.pages.split(",")]
    else:
        pages = range(args.start, args.end + 1)

    print(f"Processing {len(list(pages))} canonical pages")
    print(f"Output: {args.output}/sources/{{source_name}}/")
    print()

    # Process pages
    skip_existing = not args.no_skip
    total_processed = 0
    total_skipped = 0

    for canonical_page in pages:
        results = process_page_across_sources(
            sources, canonical_page, args.output, page_mapping
        )

        if results:
            total_processed += len(results)
        else:
            total_skipped += 1

    # Summary
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Pages processed: {total_processed}")
    print(f"Pages skipped: {total_skipped}")
    print()
    print("Output structure:")
    print(f"  {args.output}/sources/{{source_name}}/page_NNN.{{txt,json,png}}")
    print()
    print("Next steps:")
    print("  1. Review OCR outputs in phase1_ocr/sources/")
    print("  2. Run build_page_mapping.py to create equivalency map")
    print("  3. Proceed to Phase 2 with multi-source reconciliation")

    return 0


if __name__ == "__main__":
    sys.exit(main())
