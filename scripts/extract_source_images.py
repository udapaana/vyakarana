#!/usr/bin/env python3
"""Extract page images from multiple PDF sources for Claude Code OCR.

This script extracts images from each source PDF so Claude Code can:
1. View images directly (no API calls needed)
2. Transcribe interactively
3. Compare sources visually
4. Build page equivalency mapping
"""

import json
import argparse
from pathlib import Path
from typing import Dict
from pdf2image import convert_from_path
from PIL import Image
from dataclasses import dataclass

# Import preprocessing
import sys

sys.path.insert(0, str(Path(__file__).parent))
from preprocess_image import preprocess_for_ocr


@dataclass
class SourceConfig:
    """Configuration for a single PDF source."""

    name: str
    path: Path
    total_pages: int
    priority: int

    @classmethod
    def from_dict(cls, name: str, data: dict):
        """Load from config JSON."""
        return cls(
            name=name,
            path=Path(data["path"]),
            total_pages=data["total_pages"],
            priority=data["priority"],
        )


def load_source_config(
    config_path: Path = Path("config/sources.json"),
) -> Dict[str, SourceConfig]:
    """Load verified source configurations."""
    with config_path.open() as f:
        data = json.load(f)

    sources = {}
    for name, source_data in data["sources"].items():
        if source_data.get("verified", False):
            sources[name] = SourceConfig.from_dict(name, source_data)

    return sources


def extract_page_image(
    pdf_path: Path,
    page_num: int,
    output_path: Path,
    dpi: int = 300,
    preprocess: bool = True,
) -> bool:
    """Extract a single page as image."""
    try:
        if output_path.exists():
            return True

        images = convert_from_path(
            pdf_path, first_page=page_num, last_page=page_num, dpi=dpi
        )

        if not images:
            return False

        image = images[0]

        if preprocess:
            image = preprocess_for_ocr(image)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path, "PNG")

        return True

    except Exception as e:
        print(f"    Error: {e}")
        return False


def extract_source_pages(
    source: SourceConfig,
    pages: range,
    output_dir: Path,
    dpi: int = 300,
    preprocess: bool = True,
) -> int:
    """Extract multiple pages from a source."""
    source_dir = output_dir / "images" / source.name
    source_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{source.name} ({source.total_pages} pages):")
    print(f"  Output: {source_dir}/")

    extracted = 0
    skipped = 0

    for page_num in pages:
        if page_num > source.total_pages:
            break

        output_path = source_dir / f"page_{page_num:03d}.png"

        if output_path.exists():
            skipped += 1
        else:
            if extract_page_image(source.path, page_num, output_path, dpi, preprocess):
                extracted += 1

    print(f"  ✓ Extracted {extracted} pages, {skipped} cached")
    return extracted


def main():
    """Extract page images from all sources."""
    parser = argparse.ArgumentParser(
        description="Extract page images from multiple PDF sources"
    )
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--output", type=Path, default=Path("phase1_ocr"))
    parser.add_argument("--config", type=Path, default=Path("config/sources.json"))
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--no-preprocess", action="store_true")

    args = parser.parse_args()

    print("Multi-Source Image Extraction")
    print("=" * 70)

    sources = load_source_config(args.config)
    print(f"\nSources: {len(sources)}")
    for name, source in sorted(sources.items(), key=lambda x: x[1].priority):
        print(f"  {source.name}: {source.total_pages} pages")

    pages = range(args.start, args.end + 1)
    print(f"\nExtracting pages {args.start}-{args.end}\n")

    for source in sorted(sources.values(), key=lambda x: x.priority):
        extract_source_pages(
            source, pages, args.output, args.dpi, not args.no_preprocess
        )

    print(f"\nDone! Images saved to {args.output}/images/")


if __name__ == "__main__":
    main()
