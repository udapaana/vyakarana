#!/usr/bin/env python3
"""
Fix processing_status.json by reconciling with actual processed files.

This script:
1. Scans structured_pages directory for actual .md files
2. Updates processed_pages to match actual files
3. Removes duplicate error entries
4. Removes errors for pages that are now successfully processed
"""

import json
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Paths
BASE_DIR = Path("/Users/skmnktl/Downloads/ocr")
STRUCTURED_DIR = BASE_DIR / "structured_pages"
STATUS_FILE = BASE_DIR / "data" / "processing_status.json"

def get_actual_processed_pages():
    """Get list of pages that have actual .md files."""
    processed = []
    for md_file in sorted(STRUCTURED_DIR.glob("page_*.md")):
        page_num = md_file.stem  # e.g., "page_001"
        processed.append(page_num)
    return processed

def deduplicate_errors(errors):
    """
    Remove duplicate error entries, keeping only the most recent error per page.
    Returns a list of unique errors sorted by page number.
    """
    # Group errors by page
    errors_by_page = defaultdict(list)
    for error in errors:
        page = error["page"]
        errors_by_page[page].append(error)

    # Keep only most recent error per page
    unique_errors = []
    for page, page_errors in errors_by_page.items():
        # Sort by timestamp and take the most recent
        sorted_errors = sorted(page_errors, key=lambda e: e["timestamp"], reverse=True)
        unique_errors.append(sorted_errors[0])

    # Sort by page number
    unique_errors.sort(key=lambda e: e["page"])

    return unique_errors

def main():
    print("🔧 Fixing processing_status.json...")
    print()

    # Get actual processed pages
    print("📂 Scanning structured_pages directory...")
    actual_processed = get_actual_processed_pages()
    print(f"   Found {len(actual_processed)} actual .md files")
    print()

    # Load current status
    print("📖 Reading processing_status.json...")
    with open(STATUS_FILE, 'r') as f:
        status = json.load(f)

    old_processed_count = len(status.get("processed_pages", []))
    old_error_count = len(status.get("processed_with_errors", []))
    print(f"   Current: {old_processed_count} processed, {old_error_count} errors")
    print()

    # Update processed_pages to match actual files
    status["processed_pages"] = actual_processed

    # Remove errors for pages that are now successfully processed
    actual_processed_set = set(actual_processed)
    errors = status.get("processed_with_errors", [])

    print("🧹 Cleaning up errors...")
    # Remove errors for successfully processed pages
    errors = [e for e in errors if e["page"] not in actual_processed_set]
    print(f"   Removed {old_error_count - len(errors)} errors for successfully processed pages")

    # Deduplicate remaining errors
    old_error_count_before_dedup = len(errors)
    errors = deduplicate_errors(errors)
    print(f"   Removed {old_error_count_before_dedup - len(errors)} duplicate error entries")
    print(f"   Remaining errors: {len(errors)}")
    print()

    status["processed_with_errors"] = errors

    # Update metadata
    status["last_updated"] = datetime.now().isoformat()
    status["total_pages"] = 726

    # Save updated status
    print("💾 Saving updated processing_status.json...")
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f, indent=2)

    print()
    print("✅ Fixed processing_status.json")
    print()
    print("📊 Summary:")
    print(f"   Processed pages: {len(actual_processed)}/{status['total_pages']} ({len(actual_processed)*100//status['total_pages']}%)")
    print(f"   Pages with errors: {len(errors)}")
    print(f"   Pages remaining: {status['total_pages'] - len(actual_processed)}")
    print()

    # Show error breakdown by type
    if errors:
        print("❌ Error breakdown:")
        error_types = defaultdict(int)
        for error in errors:
            error_msg = error["error"]
            if "No JSON found" in error_msg:
                error_types["No JSON found"] += 1
            elif "JSON parse error" in error_msg:
                error_types["JSON parse error"] += 1
            elif "ACTION REQUIRED" in error_msg or "Consumer Terms" in error_msg:
                error_types["Terms of Service update"] += 1
            elif "CLI error code 1" in error_msg:
                error_types["CLI error (unknown)"] += 1
            else:
                error_types["Other"] += 1

        for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
            print(f"   {error_type}: {count}")
        print()

    # List pages that still need processing
    missing_pages = []
    for i in range(1, status["total_pages"] + 1):
        page_id = f"page_{i:03d}"
        if page_id not in actual_processed_set and not any(e["page"] == page_id for e in errors):
            missing_pages.append(i)

    if missing_pages:
        print(f"📋 Pages that need processing ({len(missing_pages)}):")
        # Show first 20, then ellipsis if more
        if len(missing_pages) <= 20:
            print(f"   {', '.join(map(str, missing_pages))}")
        else:
            print(f"   {', '.join(map(str, missing_pages[:20]))} ... and {len(missing_pages) - 20} more")
        print()

if __name__ == "__main__":
    main()
