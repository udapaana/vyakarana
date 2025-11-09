#!/usr/bin/env python3
"""Test that the fixed read_pages method works correctly"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "scripts" / "ai"))

from parallel_extractor import ParallelExtractor

# Initialize extractor
extractor = ParallelExtractor(
    structured_pages_dir=Path("phase2_structured"),
    output_dir=Path("phase3_rules"),
    status_file=Path("data/phase3_extraction_status.json"),
)

# Test reading pages starting from 13 (where rules 7-10 are)
print("Testing read_pages starting from page 13:")
print("=" * 80)

pages = extractor.read_pages(start_page=13, count=5)

print(f"\nRead {len(pages)} pages\n")

for i, page_content in enumerate(pages):
    # Extract rule from YAML
    import re

    rule_match = re.search(r"^rule:\s*(.+)$", page_content, re.MULTILINE)
    page_match = re.search(r"^page:\s*(.+)$", page_content, re.MULTILINE)

    rule = rule_match.group(1).strip() if rule_match else "Unknown"
    page = page_match.group(1).strip() if page_match else "Unknown"

    print(f"Page {i + 1}: {page} - Rule {rule}")

print("\n" + "=" * 80)
print("Expected to see:")
print("  Page 1: 13 - Rule § 5-6")
print("  Page 2: 13a - Rule § 7-8")
print("  Page 3: 13b - Rule § 9-10")
print("  Page 4: 14 - Rule § 11")
print("  Page 5: 15 - Rule § 12")
