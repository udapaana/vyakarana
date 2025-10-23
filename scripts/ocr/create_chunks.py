#!/usr/bin/env python3
"""
Create overlapping chunks from raw page text files.
Each chunk contains ~50-100 pages with 20 page overlap.
This ensures complete chapters aren't split across chunks.
"""

import argparse
from pathlib import Path
import re


def create_chunks(
    pages_dir: str = "raw_pages",
    output_dir: str = "chunks",
    chunk_size: int = 80,
    overlap: int = 20,
    pdf_name: str = "Higher-Sanskrit-Grammar.pdf",
):
    """
    Create overlapping chunks from page text files.

    Args:
        pages_dir: Directory with page_NNNN.txt files
        output_dir: Where to save chunk files
        chunk_size: Pages per chunk
        overlap: Pages to overlap between chunks
        pdf_name: PDF name for metadata
    """
    pages_path = Path(pages_dir)
    output_path = Path(output_dir)

    if not pages_path.exists():
        raise FileNotFoundError(f"Pages directory not found: {pages_dir}")

    output_path.mkdir(exist_ok=True)

    # Get all page files sorted by page number
    page_files = sorted(pages_path.glob("page_*.txt"),
                       key=lambda p: int(re.search(r'page_(\d+)', p.name).group(1)))

    if not page_files:
        raise ValueError(f"No page files found in {pages_dir}")

    total_pages = len(page_files)
    print(f"Found {total_pages} pages")
    print(f"Chunk size: {chunk_size} pages")
    print(f"Overlap: {overlap} pages")
    print("-" * 60)

    chunk_num = 1
    start_idx = 0

    while start_idx < total_pages:
        end_idx = min(start_idx + chunk_size, total_pages)
        chunk_pages = page_files[start_idx:end_idx]

        # Extract page numbers
        first_page = int(re.search(r'page_(\d+)', chunk_pages[0].name).group(1))
        last_page = int(re.search(r'page_(\d+)', chunk_pages[-1].name).group(1))

        # Build chunk content
        chunk_lines = []
        chunk_lines.append(f"# Chunk {chunk_num}: Pages {first_page}-{last_page}")
        chunk_lines.append("")
        chunk_lines.append(f"**Source:** {pdf_name}")
        chunk_lines.append(f"**Pages in chunk:** {len(chunk_pages)}")
        chunk_lines.append("")
        chunk_lines.append("<!-- RAW OCR - Needs cleanup and structuring -->")
        chunk_lines.append("")
        chunk_lines.append("---")
        chunk_lines.append("")

        # Add each page's content
        for page_file in chunk_pages:
            page_num = int(re.search(r'page_(\d+)', page_file.name).group(1))
            text = page_file.read_text(encoding='utf-8')

            chunk_lines.append(f"<!-- Page {page_num} -->")
            chunk_lines.append("")
            chunk_lines.append(text.strip())
            chunk_lines.append("")
            chunk_lines.append("")

        # Save chunk
        chunk_filename = f"chunk_{chunk_num:02d}_pages_{first_page:04d}-{last_page:04d}.txt"
        chunk_path = output_path / chunk_filename
        chunk_path.write_text("\n".join(chunk_lines), encoding='utf-8')

        print(f"✓ Chunk {chunk_num}: pages {first_page}-{last_page} ({len(chunk_pages)} pages) → {chunk_filename}")

        # Move to next chunk with overlap
        start_idx += (chunk_size - overlap)
        chunk_num += 1

        # Stop if we've covered all pages
        if end_idx >= total_pages:
            break

    print("-" * 60)
    print(f"Created {chunk_num - 1} chunks in {output_dir}/")
    print()
    print("Next steps:")
    print(f"  1. Review chunks in {output_dir}/")
    print("  2. Run cleanup: ./cleanup_chunks.sh")
    print("  3. Claude will structure each chunk and extract chapters")


def main():
    parser = argparse.ArgumentParser(
        description="Create overlapping chunks from page text files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default: 80 pages per chunk, 20 page overlap
  python create_chunks.py

  # Larger chunks for better chapter context
  python create_chunks.py --chunk-size 100 --overlap 30

  # Smaller chunks if Claude has context limits
  python create_chunks.py --chunk-size 50 --overlap 15

Why overlapping chunks?
  - Ensures chapters aren't split across boundaries
  - Claude sees complete chapters in context
  - Easier to extract and deduplicate later
        """
    )

    parser.add_argument(
        "--pages-dir",
        default="raw_pages",
        help="Directory with page text files (default: raw_pages/)"
    )

    parser.add_argument(
        "--output-dir",
        default="chunks",
        help="Output directory for chunks (default: chunks/)"
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=80,
        help="Pages per chunk (default: 80)"
    )

    parser.add_argument(
        "--overlap",
        type=int,
        default=20,
        help="Overlapping pages between chunks (default: 20)"
    )

    parser.add_argument(
        "--pdf-name",
        default="Higher-Sanskrit-Grammar.pdf",
        help="PDF filename for metadata"
    )

    args = parser.parse_args()

    try:
        create_chunks(
            pages_dir=args.pages_dir,
            output_dir=args.output_dir,
            chunk_size=args.chunk_size,
            overlap=args.overlap,
            pdf_name=args.pdf_name,
        )
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
