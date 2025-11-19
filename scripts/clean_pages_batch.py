#!/usr/bin/env python3
"""
Batch process pages using corrected mapping
"""

import json
import sys
from pathlib import Path

def load_mapping():
    with open('phase2_corrected_mapping.json') as f:
        return json.load(f)

def get_page_info(mapping, page_num):
    """Get info for a specific output page"""
    for entry in mapping:
        if entry['output_page'] == page_num:
            return entry
    return None

def show_batch_plan(mapping, start, end):
    """Show what will be cleaned in this batch"""
    print(f"\nBatch Plan: Pages {start:03d}-{end:03d}")
    print("=" * 80)
    print(f"{'Output':15s} {'Source':20s} {'Internal':10s} {'Content':30s}")
    print("=" * 80)
    
    for i in range(start, min(end + 1, len(mapping) + 1)):
        entry = get_page_info(mapping, i)
        if entry:
            output = entry['output_file']
            source = entry['source_file']
            internal = str(entry['internal_page']) if entry['internal_page'] else '?'
            content = entry['content_type']

            # Check if file exists
            exists = Path(f"phase2_cleaned/{output}").exists()
            status = "✓ EXISTS" if exists else "  NEW"

            print(f"{status} {output:13s} {source:20s} {internal:10s} {content:30s}")

if __name__ == '__main__':
    mapping = load_mapping()
    
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/clean_pages_batch.py START [END]")
        print("Example: python3 scripts/clean_pages_batch.py 1 20")
        sys.exit(1)
    
    start = int(sys.argv[1])
    end = int(sys.argv[2]) if len(sys.argv) > 2 else start
    
    show_batch_plan(mapping, start, end)
