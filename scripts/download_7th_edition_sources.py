#!/usr/bin/env python3
"""Download multiple digitizations of Kale's 7th edition for quality comparison.

We want the same book (7th edition) from multiple scans to select the best
quality image for each page.

Following coding standards:
- Deep module: Simple interface, complex implementation hidden
- Comments explain why: Why we need multiple scans of same edition
"""

import urllib.request
import urllib.parse
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Source:
    """Represents a potential 7th edition digitization source."""
    name: str
    archive_id: str
    filename: str
    notes: str = ""

    @property
    def url(self) -> str:
        """Construct download URL with proper encoding."""
        encoded_filename = urllib.parse.quote(self.filename)
        return f"https://archive.org/download/{self.archive_id}/{encoded_filename}"


# Why these sources: All are potential 7th edition scans
# We'll verify after download by checking title pages
POTENTIAL_7TH_EDITION: Dict[str, Source] = {
    "official_7th": Source(
        name="Official 7th Edition (1931)",
        archive_id="HigherSanskritGrammarKale7thEdition",
        filename="With bookmarks Kale,M.R.Higher Sanskrit Grammar.7th edn.1931 OCRed.pdf",
        notes="Explicitly labeled as 7th edition 1931"
    ),
    "dli_2015": Source(
        name="DLI 2015 (IGNCA Delhi)",
        archive_id="in.ernet.dli.2015.105411",
        filename="2015.105411.Higher-Sanskrit-Grammar.pdf",
        notes="729 pages, need to verify edition"
    ),
    "xmqc_1931": Source(
        name="xMqc 1931 Mulgaokar",
        archive_id="xMqc_a-higher-sanskrit-grammar-by-moreshwar-ram-chandra-kale-1931-d-v-mulgaokar",
        filename="A Higher Sanskrit Grammar By Moreshwar Ram Chandra Kale 1931 - D V Mulgaokar.pdf",
        notes="1931 date suggests 7th edition"
    ),
}


def download_source(source: Source, output_dir: Path) -> Optional[Path]:
    """Download a PDF source if not already present.

    Args:
        source: Source metadata
        output_dir: Directory to save PDF

    Returns:
        Path to downloaded file, or None if failed
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create safe filename
    safe_name = source.name.replace(" ", "_").replace("(", "").replace(")", "")
    output_path = output_dir / f"{safe_name}.pdf"

    # Skip if exists
    if output_path.exists():
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"✓ {source.name} already exists ({size_mb:.1f} MB)")
        return output_path

    print(f"\nDownloading {source.name}...")
    print(f"  From: {source.url}")
    print(f"  Notes: {source.notes}")

    try:
        urllib.request.urlretrieve(source.url, output_path)
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"  ✓ Downloaded ({size_mb:.1f} MB)")
        return output_path

    except Exception as e:
        print(f"  ✗ Failed: {e}")
        if output_path.exists():
            output_path.unlink()
        return None


def main():
    """Download all potential 7th edition sources."""
    print("="*70)
    print("Downloading Potential 7th Edition Sources")
    print("="*70)
    print("\nWhy multiple sources: Same book, different scans")
    print("Goal: Select best quality image for each page")
    print()

    output_dir = Path("source/candidates")
    successful = []
    failed = []

    for key, source in POTENTIAL_7TH_EDITION.items():
        result = download_source(source, output_dir)
        if result:
            successful.append(source.name)
        else:
            failed.append(source.name)

    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    print(f"Downloaded: {len(successful)}/{len(POTENTIAL_7TH_EDITION)}")

    if successful:
        print("\nNext steps:")
        print("  1. Run verify_7th_edition.py to check title pages")
        print("  2. Keep only verified 7th edition scans")
        print("  3. Run compare_quality.py to select best images per page")


if __name__ == "__main__":
    main()
