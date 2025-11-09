#!/usr/bin/env python3
"""
Simple sequential rule extractor using Claude CLI

Usage:
    # Extract all 972 rules
    python3 extract_rules.py

    # Extract specific range
    python3 extract_rules.py --start 1 --end 50

    # Resume from checkpoint
    python3 extract_rules.py --resume
"""

import argparse
from pathlib import Path
from scripts.ai.batch_sequential import SequentialExtractor


def main():
    parser = argparse.ArgumentParser(
        description="Extract Sanskrit grammar rules sequentially"
    )
    parser.add_argument(
        '--start',
        type=int,
        default=1,
        help='Starting rule number (default: 1)'
    )
    parser.add_argument(
        '--end',
        type=int,
        default=972,
        help='Ending rule number (default: 972)'
    )
    parser.add_argument(
        '--output',
        default='rules',
        help='Output directory (default: rules)'
    )
    parser.add_argument(
        '--pages',
        default='structured_pages',
        help='Structured pages directory (default: structured_pages)'
    )
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume from last checkpoint (ignores --start)'
    )

    args = parser.parse_args()

    print("\n" + "="*60)
    print("SEQUENTIAL RULE EXTRACTOR")
    print("="*60)
    print(f"Output: {args.output}/")
    print(f"Range: Rules {args.start}-{args.end}")
    print(f"Method: Sequential page-by-page with fresh context per rule")
    print(f"Cost: $0 (uses Claude CLI browser auth)")
    print("="*60 + "\n")

    extractor = SequentialExtractor(
        structured_pages_dir=Path(args.pages),
        output_dir=Path(args.output)
    )

    # Load checkpoint if resuming
    if args.resume:
        state = extractor.load_checkpoint()
        print(f"📁 Resuming from Rule {state.current_rule}, Page {state.current_page}\n")

    # Run extraction
    extractor.extract_all(start_rule=args.start, end_rule=args.end)

    print("\n" + "="*60)
    print("EXTRACTION COMPLETE")
    print("="*60)
    print(f"Check results: ls {args.output}/rule_*.md | wc -l")
    print(f"View checkpoint: cat {args.output}/.checkpoint.json")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
