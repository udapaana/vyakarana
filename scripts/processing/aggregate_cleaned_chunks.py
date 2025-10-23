#!/usr/bin/env python3
"""
Aggregate cleaned chunks into a single, properly structured markdown document.

Strategy for 2-page chunks with 1-page overlap:
- Chunk 1: pages 1-2
- Chunk 2: pages 2-3 (page 2 overlaps)
- etc.

Use only odd-numbered chunks (1, 3, 5, 7...) to avoid overlaps.
This gives us pages: 1-2, 3-4, 5-6, 7-8... with no overlap.
"""

import re
from pathlib import Path
import argparse
from typing import List, Tuple


def extract_chunk_number(filename: str) -> int:
    """Extract chunk number from filename like 'chunk_01_pages_0001-0002_structured.md'."""
    match = re.search(r'chunk_(\d+)_', filename)
    if match:
        return int(match.group(1))
    return 0


def normalize_structure(content: str) -> str:
    """
    Normalize markdown structure for proper hierarchy and navigation.

    Hierarchy:
    - # (h1): PREFACE, Chapters (I, II, III...)
    - ## (h2): Major sections within chapters (THE ALPHABET, RULES OF SANDHI)
    - ### (h3): Subsections (I. SVARASANDHI, II. HALSANDHI, etc.)
    - #### (h4): Section numbers (§ 1., § 2., etc.)
    """
    lines = content.split('\n')
    structured_lines = []

    for line in lines:
        # Convert "CHAPTER II." or "Chapter I." to h1
        if re.match(r'^CHAPTER\s+[IVX]+\.', line, re.IGNORECASE):
            line = '# ' + line.strip()

        # Convert all-caps section titles to h2 (but not if already a heading)
        # THE ALPHABET, RULES OF SANDHI, etc.
        elif re.match(r'^[A-Z][A-Z\s-]{3,}\.$', line) and not line.startswith('#'):
            # Skip if it's a short abbreviation list header
            if 'ABBREVIATIONS' not in line and len(line) < 50:
                line = '## ' + line.strip()

        # Convert Roman numeral subsections to h3
        # "I. SVARASANDHI", "II. HALSANDHI", etc.
        elif re.match(r'^[IVX]+\.\s+[@\[]?[A-Z]', line):
            line = '### ' + line.strip()

        # Convert section numbers to h4
        # "§ 1. Sanskrit, or..."  -> "#### § 1. Sanskrit, or..."
        elif re.match(r'^§\s*\d+\.\s+[A-Z@]', line):
            line = '#### ' + line.strip()

        structured_lines.append(line)

    return '\n'.join(structured_lines)


def clean_chunk_metadata(content: str) -> str:
    """
    Remove OCR metadata markers and formatting artifacts from chunk content.

    Removes:
    - Chunk headers, source metadata, page markers
    - Running headers with page numbers
    - Section headers with embedded page numbers
    - Stray artifacts and formatting issues
    """
    lines = content.split('\n')
    cleaned_lines = []
    skip_next = False

    for i, line in enumerate(lines):
        # Skip chunk headers
        if re.match(r'^# Chunk \d+: Pages \d+-\d+$', line):
            skip_next = True
            continue

        # Skip source metadata
        if line.startswith('**Source:**') or line.startswith('**Pages in chunk:**'):
            continue

        # Skip page markers
        if re.match(r'^<!--\s*Page \d+\s*-->$', line):
            continue

        # Skip "RAW OCR" comments
        if 'RAW OCR' in line and 'cleanup' in line:
            continue

        # Skip running headers: "4        SANSKRIT GRAMMAR                    [§ 4—"
        if re.match(r'^\s*\d+\.?\s+SANSKRIT GRAMMAR\.?\s+[@\[§]', line):
            continue

        # Skip section headers with page numbers at end
        # Patterns: "§ 13-15] THE ALPHABET. 17", "§ 19. RULES OF SANDHI. 23", "§ 23-24 | RULES OF SANDHI. 19"
        if re.match(r'^§+\s*\d+[-\d\]\.|\s]*\s+[A-Z\s]+\.\s+\d+\s*$', line):
            continue

        # Skip lines starting with @[§ XX] followed by heading and page number
        # "@[§ 20-21]  RULES OF @[Sandhi]. 15"
        if re.match(r'^@\[§\s*\d+[-\d]*\]\s+.*\.\s+\d+\s*$', line):
            continue

        # Skip standalone section references like "§§ 28-31 ] RULES OF SANDHI. 23"
        if re.match(r'^§+\s*\d+[-\d\s]+\]\s+[A-Z\s]+\.\s+\d+', line):
            continue

        # Skip separator lines that were just metadata dividers
        if skip_next and line.strip() == '---':
            skip_next = False
            continue

        # Skip empty lines at the start
        if not cleaned_lines and not line.strip():
            continue

        # Fix lines that incorrectly start with § but are actually footnotes
        # "§ @[उच्चारणार्थं...]" -> just keep as is (footnote)
        if re.match(r'^§\s+@\[[\u0900-\u097F]', line):
            # This is a Sanskrit footnote, not a section marker - remove the §
            line = line.lstrip('§').lstrip()

        cleaned_lines.append(line)
        skip_next = False

    # Post-process to remove duplicate consecutive empty lines
    final_lines = []
    prev_empty = False
    for line in cleaned_lines:
        is_empty = not line.strip()
        if is_empty and prev_empty:
            continue
        final_lines.append(line)
        prev_empty = is_empty

    # Remove trailing empty lines
    while final_lines and not final_lines[-1].strip():
        final_lines.pop()

    return '\n'.join(final_lines)


def aggregate_odd_chunks(chunks_dir: Path, output_file: Path, start_chunk: int = 1, end_chunk: int = 999999):
    """
    Aggregate only odd-numbered chunks (1, 3, 5...) to avoid overlaps.
    Produces properly structured markdown with consistent hierarchy.
    """
    # Find all structured chunk files
    chunk_files = sorted(
        chunks_dir.glob('chunk_*_structured.md'),
        key=lambda p: extract_chunk_number(p.name)
    )

    if not chunk_files:
        print(f"❌ No structured chunks found in {chunks_dir}")
        return

    # Filter for chunks in range
    chunk_files = [f for f in chunk_files
                   if start_chunk <= extract_chunk_number(f.name) <= end_chunk]

    # Filter for odd chunks
    odd_chunks = [f for f in chunk_files if extract_chunk_number(f.name) % 2 == 1]

    print(f"Found {len(chunk_files)} total chunks in range {start_chunk}-{end_chunk}")
    print(f"Using {len(odd_chunks)} odd-numbered chunks (no overlaps)")
    print(f"Cleaning and structuring content...\n")

    # Concatenate all odd chunks
    aggregated_parts = []
    for chunk_file in odd_chunks:
        content = chunk_file.read_text(encoding='utf-8')
        # Clean metadata from each chunk
        cleaned_content = clean_chunk_metadata(content)
        if cleaned_content.strip():
            aggregated_parts.append(cleaned_content)
        chunk_num = extract_chunk_number(chunk_file.name)
        print(f"✓ Added chunk {chunk_num}")

    # Join with double newline separator
    aggregated = '\n\n'.join(aggregated_parts)

    # Normalize document structure for proper markdown hierarchy
    structured = normalize_structure(aggregated)

    # Write aggregated content
    output_file.write_text(structured, encoding='utf-8')
    print(f"\n✅ Structured document written to {output_file}")
    print(f"   Total chunks: {len(odd_chunks)}")
    print(f"   Total length: {len(structured):,} characters")
    print(f"   Approx pages covered: {len(odd_chunks) * 2}")
    print(f"\n📚 Document structure:")
    print(f"   - Proper markdown headings (h1-h4)")
    print(f"   - Navigable via markdown parsers")
    print(f"   - All artifacts removed")


def aggregate_all_with_merge(chunks_dir: Path, output_file: Path, start_chunk: int = 1, end_chunk: int = 999999):
    """
    Use all chunks with overlap markers (for debugging/comparison).
    """
    chunk_files = sorted(
        chunks_dir.glob('chunk_*_structured.md'),
        key=lambda p: extract_chunk_number(p.name)
    )

    if not chunk_files:
        print(f"❌ No structured chunks found in {chunks_dir}")
        return

    # Filter for chunks in range
    chunk_files = [f for f in chunk_files
                   if start_chunk <= extract_chunk_number(f.name) <= end_chunk]

    print(f"Found {len(chunk_files)} chunks to merge with overlap handling")
    print(f"Cleaning and structuring content...\n")

    aggregated_parts = []
    for chunk_file in chunk_files:
        content = chunk_file.read_text(encoding='utf-8')
        cleaned_content = clean_chunk_metadata(content)
        if cleaned_content.strip():
            aggregated_parts.append(cleaned_content)
        chunk_num = extract_chunk_number(chunk_file.name)
        print(f"✓ Added chunk {chunk_num}")

    aggregated = '\n\n---\n\n'.join(aggregated_parts)
    structured = normalize_structure(aggregated)

    output_file.write_text(structured, encoding='utf-8')
    print(f"\n✅ Structured document written to {output_file}")
    print(f"   Total chunks: {len(chunk_files)}")
    print(f"   Total length: {len(structured):,} characters")


def main():
    parser = argparse.ArgumentParser(
        description='Aggregate cleaned chunks into a properly structured markdown document'
    )
    parser.add_argument(
        '--chunks-dir',
        type=Path,
        default=Path('structured_chapters'),
        help='Directory containing structured chunk files'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('aggregated_full.md'),
        help='Output file for aggregated content'
    )
    parser.add_argument(
        '--method',
        choices=['odd-only', 'all-with-merge'],
        default='odd-only',
        help='Aggregation method: odd-only (simple, no overlaps) or all-with-merge (use all chunks)'
    )
    parser.add_argument(
        '--start',
        type=int,
        default=1,
        help='Start from chunk N (default: 1)'
    )
    parser.add_argument(
        '--end',
        type=int,
        default=999999,
        help='End at chunk N (default: all)'
    )

    args = parser.parse_args()

    if args.method == 'odd-only':
        aggregate_odd_chunks(args.chunks_dir, args.output, args.start, args.end)
    else:
        aggregate_all_with_merge(args.chunks_dir, args.output, args.start, args.end)


if __name__ == '__main__':
    main()
