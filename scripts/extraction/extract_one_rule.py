#!/usr/bin/env python3
"""
Extract a single rule given rule number and starting page.
Outputs JSON with the extracted content and end page.
"""

import sys
import json
from pathlib import Path


def read_pages(structured_pages_dir: Path, start_page: int, num_pages: int = 10):
    """Read multiple pages starting from start_page."""
    all_pages = sorted(
        structured_pages_dir.glob('page_*.md'),
        key=lambda p: int(p.stem.split('_')[1])
    )

    pages_content = []
    page_numbers = []

    for page_file in all_pages:
        page_num = int(page_file.stem.split('_')[1])
        if page_num < start_page:
            continue
        if page_num >= start_page + num_pages:
            break

        content = page_file.read_text()
        pages_content.append(f"=== PAGE {page_num} ===\n{content}\n")
        page_numbers.append(page_num)

    return '\n'.join(pages_content), page_numbers


def main():
    if len(sys.argv) < 3:
        print("Usage: extract_one_rule.py <rule_num> <start_page>")
        sys.exit(1)

    rule_num = int(sys.argv[1])
    start_page = int(sys.argv[2])

    base_dir = Path('/Users/skmnktl/Downloads/ocr')
    structured_pages_dir = base_dir / 'structured_pages'

    pages_content, page_numbers = read_pages(structured_pages_dir, start_page)

    # Output the data for Claude to process
    print(json.dumps({
        'rule_num': rule_num,
        'start_page': start_page,
        'page_numbers': page_numbers,
        'pages_content': pages_content
    }, indent=2))


if __name__ == '__main__':
    main()
