#!/usr/bin/env python3
"""
Direct rule extraction - to be run BY Claude Code, not calling external APIs.

This script just reads pages and prints them. Claude Code (you) will then
extract the rules directly in the conversation.
"""

import yaml
from pathlib import Path
import argparse


def read_pages(pages_dir, start_page, count=10):
    """Read pages starting from start_page."""
    pages_dir = Path(pages_dir)
    all_pages = sorted(pages_dir.glob("page_*.md"), key=lambda p: int(p.stem.split("_")[1]))

    content = []
    page_nums = []

    for p in all_pages:
        n = int(p.stem.split("_")[1])
        if n < start_page:
            continue
        if n >= start_page + count:
            break
        content.append(f"=== PAGE {n} ===\n{p.read_text()}\n")
        page_nums.append(n)

    return "\n".join(content), page_nums


def write_rule(output_dir, rule_num, content, source_pages):
    """Write a rule file."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rule_file = output_dir / f"rule_{rule_num}.md"

    yaml_data = {
        'rule': f'§ {rule_num}',
        'source_pages': source_pages
    }

    with open(rule_file, 'w', encoding='utf-8') as f:
        f.write('---\n')
        f.write(yaml.dump(yaml_data, allow_unicode=True, sort_keys=False))
        f.write('---\n\n')
        f.write(content)

    print(f"✓ Written {rule_file}")
    return rule_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Helper for direct rule extraction')
    parser.add_argument('--show-pages', type=int, help='Show pages starting from this number')
    parser.add_argument('--count', type=int, default=10, help='Number of pages to show')
    parser.add_argument('--write-rule', type=int, help='Write rule number')
    parser.add_argument('--content-file', type=str, help='File containing rule content to write')
    parser.add_argument('--source-pages', type=int, nargs='+', help='Source page numbers')
    parser.add_argument('--output', type=str, default='rules', help='Output directory')

    args = parser.parse_args()

    base_dir = Path("/Users/skmnktl/Downloads/ocr")
    pages_dir = base_dir / "structured_pages"
    output_dir = base_dir / args.output

    if args.show_pages:
        # Just show pages for Claude to extract from
        content, page_nums = read_pages(pages_dir, args.show_pages, args.count)
        print(f"\nPages {page_nums[0]}-{page_nums[-1]}:\n")
        print(content)

    elif args.write_rule and args.content_file:
        # Write a rule from a content file
        content = Path(args.content_file).read_text()
        write_rule(output_dir, args.write_rule, content, args.source_pages or [])

    else:
        parser.print_help()
