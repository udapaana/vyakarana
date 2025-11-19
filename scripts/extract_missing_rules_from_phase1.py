#!/usr/bin/env python3
"""
Extract rules that were lost in Phase 2 AI cleaning, directly from Phase 1 OCR.

These rules exist in Phase 1 but were skipped during Phase 2 AI cleaning:
- § 123 (page 75)
- § 625-628 (pages 382-383)
- § 740 (page 438)
- § 840 (page 491)
- § 962 (page 530)
"""

import re
from pathlib import Path
import yaml


PHASE1_DIR = Path("/Users/skmnktl/Downloads/ocr/phase1_ocr/sources/official_1931")
PHASE3A_DIR = Path("/Users/skmnktl/Downloads/ocr/phase3_rules/core/raw")


# Map of missing rules to their source pages
MISSING_RULES = {
    123: {"start_page": 75, "end_page": 76},
    361: {"start_page": 223, "end_page": 223},
    363: {"start_page": 224, "end_page": 224},
    625: {"start_page": 382, "end_page": 382},
    626: {"start_page": 382, "end_page": 382},
    627: {"start_page": 383, "end_page": 383},
    628: {"start_page": 383, "end_page": 384},
    740: {"start_page": 437, "end_page": 438},
    839: {"start_page": 491, "end_page": 491},
    840: {"start_page": 491, "end_page": 491},
    962: {"start_page": 530, "end_page": 530},
}


def find_rule_in_text(text, rule_num):
    """Find § N marker in text (at line start only)"""
    patterns = [
        rf"^§\s*{rule_num}\.",
        rf"\n§\s*{rule_num}\.",
        rf"^§\s*{rule_num}\s",
        rf"\n§\s*{rule_num}\s",
        rf"^Obs\.\s*§\s*{rule_num}\.",  # For § 962 which is marked "Obs."
        rf"\nObs\.\s*§\s*{rule_num}\.",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            if pattern.startswith(r"\n"):
                return match.start() + 1
            else:
                return match.start()

    return None


def extract_phase1_rule(rule_num, start_page, end_page):
    """Extract a rule from Phase 1 OCR"""

    # Read all pages in range
    all_text = []
    pages = []

    for page_num in range(start_page, end_page + 1):
        page_file = PHASE1_DIR / f"{page_num:03d}.txt"
        if not page_file.exists():
            print(f"  WARNING: Page {page_num} not found")
            continue

        text = page_file.read_text(encoding="utf-8")
        all_text.append(text)
        pages.append(f"{page_num:03d}")

    full_text = "\n\n".join(all_text)

    # Find rule start
    rule_start = find_rule_in_text(full_text, rule_num)
    if rule_start is None:
        print(f"  ERROR: Could not find § {rule_num} marker")
        return None

    # Find next rule end (§ N+1)
    rule_end = find_rule_in_text(full_text[rule_start:], rule_num + 1)

    if rule_end is not None:
        content = full_text[rule_start : rule_start + rule_end].strip()
    else:
        # No next rule found, take rest of text
        content = full_text[rule_start:].strip()

    return {
        "content": content,
        "page_numbers": pages,
        "page_start": int(pages[0]),
        "page_end": int(pages[-1]),
    }


def create_rule_file(rule_num, rule_data):
    """Create Stage 3A rule file"""

    output_file = PHASE3A_DIR / f"rule_{rule_num:03d}.md"

    # Create frontmatter
    frontmatter = {
        "rule_number": rule_num,
        "rule_id": f"§ {rule_num}",
        "page_start": rule_data["page_start"],
        "page_end": rule_data["page_end"],
        "source_pages": rule_data["page_numbers"],
        "extraction_status": "raw",
        "source": "phase1_direct",  # Mark as directly from Phase 1
        "note": "This rule was lost in Phase 2 AI cleaning and extracted directly from Phase 1 OCR",
    }

    # Assemble file
    file_content = "---\n"
    file_content += yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
    file_content += "---\n\n"
    file_content += rule_data["content"]

    output_file.write_text(file_content, encoding="utf-8")
    print(
        f"  ✓ Extracted Rule {rule_num:03d} from Phase 1 (pages {rule_data['page_start']}-{rule_data['page_end']})"
    )


def main():
    print("\n" + "=" * 70)
    print("EXTRACTING MISSING RULES FROM PHASE 1 OCR")
    print("=" * 70 + "\n")

    PHASE3A_DIR.mkdir(parents=True, exist_ok=True)

    for rule_num, page_info in sorted(MISSING_RULES.items()):
        print(f"\nExtracting § {rule_num}...")

        rule_data = extract_phase1_rule(
            rule_num, page_info["start_page"], page_info["end_page"]
        )

        if rule_data:
            create_rule_file(rule_num, rule_data)
        else:
            print(f"  ✗ Failed to extract rule {rule_num}")

    print("\n" + "=" * 70)
    print(f"Extraction complete: {len(MISSING_RULES)} rules recovered from Phase 1")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
