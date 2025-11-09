#!/usr/bin/env python3
"""
Reprocess failed or specific rules from Phase 3 extraction

Usage:
    # Retry all errored rules
    python3 scripts/utilities/reprocess_rules.py --retry-errors

    # Reprocess specific rule
    python3 scripts/utilities/reprocess_rules.py --rule 7

    # Reprocess range of rules
    python3 scripts/utilities/reprocess_rules.py --range 1-10

    # Show extraction status
    python3 scripts/utilities/reprocess_rules.py --status
"""

import json
import sys
from pathlib import Path
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "ai"))

from parallel_extractor import ParallelExtractor


def load_status(status_file: Path) -> dict:
    """Load extraction status"""
    if not status_file.exists():
        print(f"❌ Status file not found: {status_file}")
        sys.exit(1)

    with open(status_file) as f:
        return json.load(f)


def show_status(status_file: Path):
    """Display extraction status"""
    status = load_status(status_file)

    print("=" * 70)
    print("PHASE 3 EXTRACTION STATUS")
    print("=" * 70)
    print(f"\nTotal rules: {status['total_rules']}")
    print(
        f"Extracted: {status['total_extracted']} ({status['total_extracted'] / status['total_rules'] * 100:.1f}%)"
    )
    print(f"Errors: {status['total_errors']}")
    print(f"Remaining: {status['total_rules'] - status['total_extracted']}")
    print(f"Last updated: {status.get('last_updated', 'Never')}")

    if status["errors"]:
        print(f"\n" + "=" * 70)
        print("ERRORED RULES")
        print("=" * 70)

        for rule_num, error_info in sorted(
            status["errors"].items(), key=lambda x: int(x[0])
        ):
            print(f"\n§ {rule_num}")
            print(f"  Error: {error_info['error']}")
            print(f"  Page: {error_info['page_start']}")
            print(f"  Retries: {error_info.get('retry_count', 0)}")
            print(f"  Time: {error_info['timestamp']}")


def find_page_for_rule(rule_num: int, structured_dir: Path) -> int:
    """Find which page contains a given rule (returns base page number)"""
    import re

    for page_file in sorted(structured_dir.glob("page_*.md")):
        with open(page_file) as f:
            content = f.read(1000)

        # Check YAML for rule number
        match = re.search(r'rule:\s*["\']?.*?§\s*(\d+)', content)
        if match:
            yaml_rule = int(match.group(1))
            if yaml_rule == rule_num:
                # Extract base page number (ignoring suffix)
                page_match = re.search(r"page_(\d+)", page_file.name)
                return int(page_match.group(1))

        # Check for range (e.g., § 7-8)
        match = re.search(r'rule:\s*["\']?.*?§\s*(\d+)\s*[-–]\s*(\d+)', content)
        if match:
            start, end = int(match.group(1)), int(match.group(2))
            if start <= rule_num <= end:
                # Extract base page number (ignoring suffix)
                page_match = re.search(r"page_(\d+)", page_file.name)
                return int(page_match.group(1))

    return 1  # Default to page 1 if not found


def reprocess_rule(rule_num: int, extractor: ParallelExtractor):
    """Reprocess a single rule"""
    print(f"\n🔄 Reprocessing Rule § {rule_num}...")

    # Find starting page
    start_page = find_page_for_rule(rule_num, extractor.structured_pages_dir)

    print(f"   Starting from page {start_page}")

    try:
        # Extract the rule
        content, end_page = extractor.extract_rule(rule_num, start_page)

        # Validate
        if not extractor.validate_extracted_content(rule_num, content):
            print(f"   ❌ Validation failed")
            extractor.mark_rule_error(rule_num, "Validation failed", start_page)
            return False

        # Save
        rule_file = extractor.output_dir / f"rule_{rule_num:03d}.md"
        with open(rule_file, "w", encoding="utf-8") as f:
            f.write(content)

        # Mark as extracted
        extractor.mark_rule_extracted(rule_num, start_page, end_page)

        print(f"   ✅ Successfully extracted (page {start_page} → {end_page})")
        return True

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        extractor.mark_rule_error(rule_num, str(e), start_page)
        return False


def main():
    parser = argparse.ArgumentParser(description="Reprocess Phase 3 extraction rules")
    parser.add_argument("--status", action="store_true", help="Show extraction status")
    parser.add_argument(
        "--retry-errors", action="store_true", help="Retry all errored rules"
    )
    parser.add_argument("--rule", type=int, help="Reprocess specific rule number")
    parser.add_argument("--range", type=str, help="Reprocess range (e.g., 1-10)")
    parser.add_argument(
        "--status-file",
        type=str,
        default="data/phase3_extraction_status.json",
        help="Status file path",
    )
    parser.add_argument(
        "--output-dir", type=str, default="phase3_rules", help="Output directory"
    )

    args = parser.parse_args()

    status_file = Path(args.status_file)

    # Show status
    if args.status:
        show_status(status_file)
        return

    # Initialize extractor
    extractor = ParallelExtractor(
        structured_pages_dir=Path("phase2_structured"),
        output_dir=Path(args.output_dir),
        status_file=status_file,
    )

    # Retry errors
    if args.retry_errors:
        errored = extractor.get_errored_rules()
        if not errored:
            print("✅ No errored rules to retry")
            return

        print(f"Found {len(errored)} errored rules to retry\n")
        success = 0
        failed = 0

        for rule_num in sorted(errored):
            if reprocess_rule(rule_num, extractor):
                success += 1
            else:
                failed += 1

        print(f"\n{'=' * 70}")
        print(f"RETRY SUMMARY")
        print(f"{'=' * 70}")
        print(f"✅ Success: {success}")
        print(f"❌ Failed: {failed}")
        return

    # Process specific rule
    if args.rule:
        reprocess_rule(args.rule, extractor)
        return

    # Process range
    if args.range:
        try:
            start, end = map(int, args.range.split("-"))
            print(f"Reprocessing rules {start}-{end}\n")

            success = 0
            failed = 0

            for rule_num in range(start, end + 1):
                if reprocess_rule(rule_num, extractor):
                    success += 1
                else:
                    failed += 1

            print(f"\n{'=' * 70}")
            print(f"RANGE SUMMARY")
            print(f"{'=' * 70}")
            print(f"✅ Success: {success}")
            print(f"❌ Failed: {failed}")

        except ValueError:
            print("❌ Invalid range format. Use: --range 1-10")
            sys.exit(1)
        return

    # No action specified
    parser.print_help()


if __name__ == "__main__":
    main()
