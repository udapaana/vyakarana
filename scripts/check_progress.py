#!/usr/bin/env python3
"""
Quick progress check for rule cleanup
"""

from pathlib import Path
import json

def check_progress():
    # Count cleaned files
    all_rules = set(range(1, 973))
    cleaned = set()

    if Path('rules_cleaned').exists():
        for f in Path('rules_cleaned').glob('*.md'):
            cleaned.add(int(f.stem))

    missing = sorted(all_rules - cleaned)

    # Load progress file
    if Path('cleanup_progress.json').exists():
        with open('cleanup_progress.json') as f:
            progress = json.load(f)
    else:
        progress = {'completed': [], 'failed': [], 'skipped': []}

    print("="*60)
    print("CLEANUP PROGRESS")
    print("="*60)
    print(f"Total rules: 972")
    print(f"Cleaned files: {len(cleaned)}")
    print(f"Missing: {len(missing)}")
    print()
    print(f"Progress tracking:")
    print(f"  Completed: {len(progress['completed'])}")
    print(f"  Skipped (placeholders): {len(progress['skipped'])}")
    print(f"  Failed: {len(progress['failed'])}")

    percent = (len(cleaned) / 972) * 100
    print(f"\nOverall: {percent:.1f}% complete")

    if progress['failed']:
        print(f"\nFailed rules that need retry:")
        print(f"  {', '.join('§' + str(r) for r in sorted(progress['failed']))}")

    if len(missing) > 0 and len(missing) <= 20:
        print(f"\nRemaining rules:")
        print(f"  {', '.join('§' + str(r) for r in missing)}")
    elif len(missing) > 20:
        # Show first 10 and last 10
        first_10 = missing[:10]
        last_10 = missing[-10:]
        print(f"\nNext to process:")
        print(f"  {', '.join('§' + str(r) for r in first_10)}")
        print(f"  ... ({len(missing) - 20} more) ...")
        print(f"  {', '.join('§' + str(r) for r in last_10)}")

if __name__ == '__main__':
    check_progress()
