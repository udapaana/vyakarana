#!/usr/bin/env python3
"""
Stage 3A: Raw Rule Extraction with Proper Boundary Detection

Extracts individual rules from Phase 2 cleaned pages with minimal schema.
KEY FIX: Only includes content from § N marker onward, not preceding text.

Usage: python3 scripts/extract_rules_stage3a.py <start_rule> <end_rule>
Example: python3 scripts/extract_rules_stage3a.py 1 50
"""

import re
import sys
from pathlib import Path
import yaml

# Paths
PHASE2_DIR = Path("/Users/skmnktl/Downloads/ocr/phase2_cleaned")
PHASE3A_DIR = Path("/Users/skmnktl/Downloads/ocr/phase3_rules/core/raw")


def parse_frontmatter(content):
    """Extract YAML frontmatter from markdown file"""
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
    if not match:
        return None, content

    frontmatter = yaml.safe_load(match.group(1))
    body = match.group(2)
    return frontmatter, body


def find_rule_marker(text, rule_num):
    """
    Find the position of § N marker in text.

    IMPORTANT: Only matches rule START markers, not cross-references.
    A rule marker must be at the start of a line (possibly after whitespace).
    Cross-references like "(See § 3. a.)" won't match.
    """
    # Try various patterns for § marker (OCR variations)
    # ^ or \n ensures it's at line start
    # Matches with or without period after number
    patterns = [
        rf"^§\s*{rule_num}\.",  # § 4. at line start (with period)
        rf"\n§\s*{rule_num}\.",  # § 4. after newline (with period)
        rf"^§\s*{rule_num}\s",  # § 4 at line start (no period, with space)
        rf"\n§\s*{rule_num}\s",  # § 4 after newline (no period, with space)
        rf"^§{rule_num}\.",  # §4. at line start (with period)
        rf"\n§{rule_num}\.",  # §4. after newline (with period)
        rf"^§{rule_num}\s",  # §4 at line start (no period, with space)
        rf"\n§{rule_num}\s",  # §4 after newline (no period, with space)
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            # If pattern starts with \n, adjust position to after the newline
            if pattern.startswith(r"\n"):
                return match.start() + 1  # +1 to skip the \n
            else:
                return match.start()

    return None


def extract_rule_content(rule_num, phase2_dir, debug=False):
    """
    Extract content for a single rule by:
    1. Finding start page (where § N begins per rules_starting)
    2. Reading forward page-by-page until § N+1 is found
    3. Extracting from § N marker to § N+1 boundary

    NOTE: Does not rely on rules_continuing metadata (incomplete in Phase 2).
    Instead, reads forward until next rule marker is found.
    """

    # Find the page where this rule starts
    start_page = None
    all_pages = sorted(phase2_dir.glob("page_*.md"))

    if debug:
        print(f"\n[DEBUG] Looking for rule {rule_num}")
        print(f"[DEBUG] Total pages found: {len(all_pages)}")

    for page_file in all_pages:
        # Skip appendix pages (535+) to avoid § N numbering conflicts with prosody rules
        page_num = int(page_file.stem.split("_")[1])

        if debug and 500 <= page_num <= 505:
            print(f"[DEBUG] Checking page {page_num}")

        if page_num >= 535:
            if debug and page_num == 535:
                print(f"[DEBUG] Reached appendix cutoff at page {page_num}")
            continue

        content = page_file.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(content)

        if not fm:
            if debug:
                print(f"[DEBUG] Page {page_num} has no frontmatter")
            continue

        # Check if rule starts on this page
        rules_starting = fm.get("rules_starting", [])

        if debug and 500 <= page_num <= 505:
            print(f"[DEBUG] Page {page_num} rules_starting: {rules_starting}")

        if f"§ {rule_num}" in rules_starting:
            start_page = page_file
            if debug:
                print(f"[DEBUG] Found rule {rule_num} starting on page {page_num}")
            break

    if not start_page:
        if debug:
            print(f"[DEBUG] No start page found for rule {rule_num}")
        return None

    # Now read forward from start_page until we find § N+1
    # (Don't rely on rules_continuing which is incomplete in Phase 2)
    pages_with_rule = []
    start_page_num = int(start_page.stem.split("_")[1])

    for page_file in all_pages:
        page_num = int(page_file.stem.split("_")[1])

        # Skip pages before start page
        if page_num < start_page_num:
            continue

        # Skip appendix pages
        if page_num >= 535:
            break

        # Add this page
        pages_with_rule.append(page_file)

        # Check if this page contains § N+1 (next rule start)
        content = page_file.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(content)

        if fm and f"§ {rule_num + 1}" in fm.get("rules_starting", []):
            # Found next rule, stop here
            break

        # Safety limit: don't read more than 10 pages for a single rule
        if len(pages_with_rule) >= 10:
            break

    # Extract content from each page
    full_content = []
    page_numbers = []
    first_page = True

    for page_file in pages_with_rule:
        content = page_file.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(content)
        page_numbers.append(f"{fm['page_number']:03d}")

        if first_page:
            # On first page, find § N marker and extract from there
            marker_pos = find_rule_marker(body, rule_num)

            if marker_pos is None:
                print(
                    f"WARNING: Could not find § {rule_num} marker on page {fm['page_number']}"
                )
                # Fallback: include all content (old behavior)
                full_content.append(body)
            else:
                # Extract from § N onward
                full_content.append(body[marker_pos:])

            first_page = False
        else:
            # On continuation pages, include all content
            full_content.append(body)

    # Join content
    joined_content = "\n\n".join(full_content)

    # Trim at § N+1 marker (next rule start)
    next_rule_marker_pos = find_rule_marker(joined_content, rule_num + 1)
    if next_rule_marker_pos is not None:
        # Don't include § N+1 and beyond
        joined_content = joined_content[:next_rule_marker_pos].rstrip()

    return {
        "content": joined_content,
        "page_numbers": page_numbers,
        "page_start": int(page_numbers[0]),
        "page_end": int(page_numbers[-1]),
    }


def create_rule_file(rule_num, rule_data, output_dir):
    """Create Stage 3A rule file with minimal schema"""

    output_file = output_dir / f"rule_{rule_num:03d}.md"

    # Create frontmatter
    frontmatter = {
        "rule_number": rule_num,
        "rule_id": f"§ {rule_num}",
        "page_start": rule_data["page_start"],
        "page_end": rule_data["page_end"],
        "source_pages": rule_data["page_numbers"],
        "extraction_status": "raw",
    }

    # Assemble file
    file_content = "---\n"
    file_content += yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
    file_content += "---\n\n"
    file_content += rule_data["content"]

    output_file.write_text(file_content, encoding="utf-8")
    print(
        f"✓ Extracted Rule {rule_num:03d} ({rule_data['page_start']} → {rule_data['page_end']})"
    )


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 scripts/extract_rules_stage3a.py <start_rule> <end_rule>")
        print("Example: python3 scripts/extract_rules_stage3a.py 1 50")
        sys.exit(1)

    start_rule = int(sys.argv[1])
    end_rule = int(sys.argv[2])

    print(f"\n{'=' * 70}")
    print(f"STAGE 3A: RAW RULE EXTRACTION (Rules {start_rule}-{end_rule})")
    print(f"{'=' * 70}\n")

    # Ensure output directory exists
    PHASE3A_DIR.mkdir(parents=True, exist_ok=True)

    # Extract each rule
    for rule_num in range(start_rule, end_rule + 1):
        # Enable debug for problematic rules
        debug = rule_num in [625, 626, 627, 628, 840, 859, 860]
        rule_data = extract_rule_content(rule_num, PHASE2_DIR, debug=debug)

        if rule_data is None:
            print(f"✗ Rule {rule_num:03d}: No source pages found")
            continue

        create_rule_file(rule_num, rule_data, PHASE3A_DIR)

    print(f"\n{'=' * 70}")
    print(f"Extraction complete: {end_rule - start_rule + 1} rules processed")
    print(f"Output directory: {PHASE3A_DIR}")
    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    main()
