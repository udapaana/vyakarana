#!/usr/bin/env python3
"""
Validate Stage 3B batch completion status.

This script checks which batches of rules have been cleaned and provides
a status report that can be used to update README.md or for parallel agents
to identify which batches are available for processing.
"""

import os
import sys
from pathlib import Path
from collections import defaultdict

# Define batch ranges
BATCHES = [
    ("Batch 01", 1, 80, "§ 1-80", "Alphabet, Sandhi"),
    ("Batch 02", 81, 180, "§ 81-180", "Declension"),
    ("Batch 03", 181, 280, "§ 181-280", "Pronouns, Numerals, Compounds"),
    ("Batch 04", 281, 380, "§ 281-380", "Compounds, Taddhita, Gender, Avyayas, Verbs intro"),
    ("Batch 05", 381, 480, "§ 381-480", "Verbs: conjugation classes"),
    ("Batch 06", 481, 580, "§ 481-580", "Verbs continued"),
    ("Batch 07", 581, 680, "§ 581-680", "Verbs, Formation of Nouns"),
    ("Batch 08", 681, 780, "§ 681-780", "Accents, Vedic Grammar"),
    ("Batch 09", 781, 880, "§ 781-880", "Vedic Grammar, Syntax"),
    ("Batch 10", 881, 972, "§ 881-972", "Syntax"),
]

APPENDIX_BATCH = ("Appendix", 1, 14, "§ 1-14", "Prosody rules")


def find_project_root():
    """Find the project root directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "phase3_rules").exists():
            return current
        current = current.parent
    return None


def check_batch_status(start, end, batch_type="core"):
    """Check how many rules in a batch range are complete."""
    project_root = find_project_root()
    if not project_root:
        print("Error: Could not find project root (looking for phase3_rules/)")
        sys.exit(1)

    if batch_type == "core":
        cleaned_dir = project_root / "phase3_rules" / "core" / "cleaned"
    else:  # appendix
        cleaned_dir = project_root / "phase3_rules" / "appendix_prosody" / "cleaned"

    if not cleaned_dir.exists():
        return 0, []

    completed = []
    missing = []

    for rule_num in range(start, end + 1):
        rule_file = cleaned_dir / f"rule_{rule_num}.md"
        if rule_file.exists():
            completed.append(rule_num)
        else:
            missing.append(rule_num)

    return len(completed), missing


def get_status_emoji(completed, total):
    """Get status emoji based on completion percentage."""
    if completed == 0:
        return "⏳ PENDING"
    elif completed == total:
        return "✅ COMPLETE"
    else:
        return "🔄 IN PROGRESS"


def main():
    print("=" * 80)
    print("Stage 3B Batch Validation Report")
    print("=" * 80)
    print()

    total_complete = 0
    total_rules = 0
    batch_statuses = []

    print("Core Rules - Main Grammar (972 rules)")
    print("-" * 80)
    print(f"{'Batch':<12} {'Range':<12} {'Status':<18} {'Progress':<15} {'Notes':<25}")
    print("-" * 80)

    for batch_name, start, end, range_str, notes in BATCHES:
        batch_size = end - start + 1
        completed, missing = check_batch_status(start, end, "core")
        status = get_status_emoji(completed, batch_size)
        progress = f"{completed}/{batch_size} ({completed*100//batch_size}%)"

        print(f"{batch_name:<12} {range_str:<12} {status:<18} {progress:<15} {notes:<25}")

        total_complete += completed
        total_rules += batch_size

        batch_statuses.append({
            "name": batch_name,
            "range": range_str,
            "status": status,
            "completed": completed,
            "total": batch_size,
            "missing": missing[:5] if len(missing) <= 5 else missing[:5] + ["..."]
        })

    print("-" * 80)
    print()

    print("Appendix Prosody (14 rules)")
    print("-" * 80)
    batch_name, start, end, range_str, notes = APPENDIX_BATCH
    batch_size = end - start + 1
    completed, missing = check_batch_status(start, end, "appendix")
    status = get_status_emoji(completed, batch_size)
    progress = f"{completed}/{batch_size} ({completed*100//batch_size if batch_size > 0 else 0}%)"

    print(f"{batch_name:<12} {range_str:<12} {status:<18} {progress:<15} {notes:<25}")
    print("-" * 80)
    print()

    total_complete += completed
    total_rules += batch_size

    print("=" * 80)
    print("Summary Statistics")
    print("=" * 80)
    print(f"Total Rules Complete: {total_complete}/{total_rules} ({total_complete*100//total_rules}%)")
    print(f"Total Batches: {len(BATCHES) + 1}")
    print(f"Complete Batches: {sum(1 for b in batch_statuses if 'COMPLETE' in b['status'])}")
    print(f"In Progress Batches: {sum(1 for b in batch_statuses if 'IN PROGRESS' in b['status'])}")
    print(f"Pending Batches: {sum(1 for b in batch_statuses if 'PENDING' in b['status'])}")
    print()

    # Show details for in-progress batches
    in_progress = [b for b in batch_statuses if 'IN PROGRESS' in b['status']]
    if in_progress:
        print("=" * 80)
        print("In-Progress Batch Details")
        print("=" * 80)
        for batch in in_progress:
            print(f"\n{batch['name']} ({batch['range']}): {batch['completed']}/{batch['total']} complete")
            if batch['missing']:
                print(f"  Missing rules: {', '.join(map(str, batch['missing']))}")
        print()

    # Suggest next batch for parallel agents
    pending = [b for b in batch_statuses if 'PENDING' in b['status']]
    if pending:
        print("=" * 80)
        print("Suggested Batches for Parallel Processing")
        print("=" * 80)
        for i, batch in enumerate(pending[:3], 1):
            print(f"{i}. {batch['name']} ({batch['range']}) - {batch['total']} rules")
        print()
        print("To claim a batch: Update README.md to mark it as 🔄 IN PROGRESS")
        print()


if __name__ == "__main__":
    main()
