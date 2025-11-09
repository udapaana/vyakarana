#!/usr/bin/env python3
"""
Structure the missing OCR files that weren't processed in Phase 2

Reads OCR output and creates structured markdown files with:
- YAML frontmatter
- Proper formatting
- Cross-references
- Metadata
"""

import re
import json
from pathlib import Path
from datetime import datetime


def read_ocr_files(page_num):
    """Read both Claude and Google OCR for a page"""
    claude_file = Path(f"phase1_ocr/claude/page_{page_num:03d}.txt")
    google_file = Path(f"phase1_ocr/google/page_{page_num:03d}.txt")

    claude_text = ""
    google_text = ""

    if claude_file.exists():
        with open(claude_file) as f:
            claude_text = f.read()

    if google_file.exists():
        with open(google_file) as f:
            google_text = f.read()

    # Prefer Claude for structure, Google for Devanagari accuracy
    return claude_text, google_text


def extract_metadata(text):
    """Extract metadata from OCR text"""
    metadata = {"rules": [], "chapter": "", "section": "", "page": None}

    # Extract rule numbers
    rule_pattern = r"§\s*(\d+)(?:\s*[-–]\s*(\d+))?"
    for match in re.finditer(rule_pattern, text[:500]):
        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) else start
        metadata["rules"].extend(range(start, end + 1))

    metadata["rules"] = sorted(set(metadata["rules"]))

    # Extract chapter from headers
    lines = text.split("\n")
    for line in lines[:20]:
        line_upper = line.upper()
        if any(
            chapter in line_upper
            for chapter in ["ALPHABET", "SANDHI", "GENDER", "DECLENSION", "CONJUGATION"]
        ):
            metadata["chapter"] = line.strip()
            break

    # Extract page number
    page_match = re.search(r"\[?\s*§.*?\]\s*(\d+)", text[:200])
    if page_match:
        metadata["page"] = int(page_match.group(1))

    return metadata


def create_structured_page(page_num, claude_text, google_text, metadata):
    """Create structured markdown with YAML frontmatter"""

    # Determine rule designation
    if len(metadata["rules"]) == 1:
        rule_str = f"§ {metadata['rules'][0]}"
    elif len(metadata["rules"]) > 1:
        rule_str = f"§§ {metadata['rules'][0]}-{metadata['rules'][-1]}"
    else:
        rule_str = f"page {page_num}"

    # Build YAML frontmatter
    yaml = f"""---
rule: {rule_str}
page: {metadata["page"] or page_num}
chapter: "{metadata["chapter"] or "Unknown"}"
section: grammar
ocr_source: dual
structured_date: {datetime.now().isoformat()}
image: /images/page_{page_num:03d}.jpg
---

"""

    # Clean and format the content
    content = claude_text.strip()

    # Add section headers for rules
    for rule_num in metadata["rules"]:
        # Look for rule number and add proper markdown heading
        content = re.sub(rf"(§\s*{rule_num}\b[^#\n]*)", rf"## \1", content, count=1)

    return yaml + content


def main():
    print("Structuring missing OCR files...")
    print("=" * 70)

    # Load the mapping
    mapping_file = Path("ocr_to_missing_rules_map.txt")
    if not mapping_file.exists():
        print("Error: ocr_to_missing_rules_map.txt not found")
        print("Run the mapping script first")
        return

    # Parse mapping
    ocr_files_to_process = set()
    with open(mapping_file) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split("\t")
            if parts:
                ocr_file = parts[0].strip()
                # Extract page number from filename
                match = re.search(r"page_(\d+)", ocr_file)
                if match:
                    ocr_files_to_process.add(int(match.group(1)))

    print(f"Processing {len(ocr_files_to_process)} OCR files\n")

    output_dir = Path("phase2_structured_new")
    output_dir.mkdir(exist_ok=True)

    success = 0
    errors = 0

    for page_num in sorted(ocr_files_to_process):
        try:
            print(f"Processing page_{page_num:03d}...", end=" ")

            # Read OCR
            claude_text, google_text = read_ocr_files(page_num)

            if not claude_text:
                print("❌ No OCR text found")
                errors += 1
                continue

            # Extract metadata
            metadata = extract_metadata(claude_text)

            # Create structured page
            structured = create_structured_page(
                page_num, claude_text, google_text, metadata
            )

            # Save
            output_file = output_dir / f"page_{page_num:03d}.md"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(structured)

            rules_str = f"§ {metadata['rules']}" if metadata["rules"] else "no rules"
            print(f"✓ {rules_str}")
            success += 1

        except Exception as e:
            print(f"❌ Error: {e}")
            errors += 1

    print("\n" + "=" * 70)
    print(f"✅ Successfully structured: {success} pages")
    print(f"❌ Errors: {errors} pages")
    print(f"\nOutput directory: {output_dir}/")
    print("\nNext step: Copy these to phase2_structured/ with correct numbering")


if __name__ == "__main__":
    main()
