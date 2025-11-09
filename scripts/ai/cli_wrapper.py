#!/usr/bin/env python3
"""
Command-line interface using Claude CLI (subscription-based)

Usage:
    # Extract all rules (no API costs!)
    python -m scripts.ai.cli_wrapper extract-all --output rules

    # Extract specific range
    python -m scripts.ai.cli_wrapper extract-range 1 50 --output rules_test

    # Extract single rule
    python -m scripts.ai.cli_wrapper extract-one 77 --output rules_test --start-page 50
"""

import argparse
import sys
from pathlib import Path

from .cli_client import ClaudeCLIClient
from .batch_cli import BatchProcessorCLI
from .conversation import ConversationManager


def cmd_extract_all(args):
    """Extract all 972 rules"""
    output_dir = Path(args.output)
    structured_pages = Path(args.pages) if args.pages else Path("structured_pages")

    print(f"📚 Extracting all 972 rules (using Claude CLI)")
    print(f"📁 Input: {structured_pages}")
    print(f"📁 Output: {output_dir}")
    print(f"💰 Cost: $0 (subscription-based)")

    # Initialize processor
    processor = BatchProcessorCLI(
        structured_pages_dir=structured_pages,
        output_dir=output_dir,
    )

    # Process all rules
    processor.process_batch(start_rule=1, end_rule=972)


def cmd_extract_range(args):
    """Extract a range of rules"""
    start, end = args.start, args.end
    output_dir = Path(args.output)
    structured_pages = Path(args.pages) if args.pages else Path("structured_pages")

    print(f"📚 Extracting rules {start}-{end} (using Claude CLI)")
    print(f"📁 Input: {structured_pages}")
    print(f"📁 Output: {output_dir}")
    print(f"💰 Cost: $0 (subscription-based)")

    # Initialize processor
    processor = BatchProcessorCLI(
        structured_pages_dir=structured_pages,
        output_dir=output_dir,
    )

    # Process range
    processor.process_batch(start_rule=start, end_rule=end)


def cmd_extract_one(args):
    """Extract a single rule"""
    rule_num = args.rule
    output_dir = Path(args.output)
    structured_pages = Path(args.pages) if args.pages else Path("structured_pages")

    print(f"📚 Extracting rule {rule_num} (using Claude CLI)")

    # Initialize processor
    processor = BatchProcessorCLI(
        structured_pages_dir=structured_pages,
        output_dir=output_dir,
    )

    # Extract single rule
    result = processor.extract_rule(
        rule_number=rule_num,
        start_page=args.start_page or 1,
    )

    if result.success:
        processor.save_rule(result)
        print(f"✓ Rule {rule_num} extracted successfully")
        print(f"  End page: {result.end_page}")
        print(f"  Output: {output_dir / f'rule_{rule_num:03d}.md'}")
        print(f"💰 Cost: $0 (subscription-based)")
    else:
        print(f"✗ Failed to extract rule {rule_num}: {result.error}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Claude CLI Wrapper for Rule Extraction (Subscription-based)"
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # extract-all command
    p_all = subparsers.add_parser('extract-all', help='Extract all 972 rules')
    p_all.add_argument('--output', default='rules', help='Output directory')
    p_all.add_argument('--pages', help='Structured pages directory')

    # extract-range command
    p_range = subparsers.add_parser('extract-range', help='Extract range of rules')
    p_range.add_argument('start', type=int, help='Start rule number')
    p_range.add_argument('end', type=int, help='End rule number')
    p_range.add_argument('--output', default='rules', help='Output directory')
    p_range.add_argument('--pages', help='Structured pages directory')

    # extract-one command
    p_one = subparsers.add_parser('extract-one', help='Extract single rule')
    p_one.add_argument('rule', type=int, help='Rule number')
    p_one.add_argument('--output', default='rules_test', help='Output directory')
    p_one.add_argument('--pages', help='Structured pages directory')
    p_one.add_argument('--start-page', type=int, help='Starting page number')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Route to command handler
    commands = {
        'extract-all': cmd_extract_all,
        'extract-range': cmd_extract_range,
        'extract-one': cmd_extract_one,
    }

    commands[args.command](args)


if __name__ == '__main__':
    main()
