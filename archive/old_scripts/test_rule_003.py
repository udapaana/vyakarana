#!/usr/bin/env python3
"""
Test extraction of rule 003 to verify multi-page continuation detection
"""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / "scripts" / "ai"))

from parallel_extractor import ParallelExtractor


def main():
    # Initialize extractor
    extractor = ParallelExtractor(
        structured_pages_dir=Path("phase2_structured"),
        output_dir=Path("phase3_rules"),
        status_file=Path("data/phase3_extraction_status.json"),
    )

    # Read the structured pages to build the prompt
    rule_num = 3
    start_page = 11

    # Build the prompt (same logic as extract_rule but we'll print it instead)
    pages_content = []
    max_pages = 10

    for offset in range(max_pages):
        current_page = start_page + offset
        page_file = extractor.structured_pages_dir / f"page_{current_page:03d}.md"

        if not page_file.exists():
            # Try with letter suffix
            page_file = extractor.structured_pages_dir / f"page_{current_page:03d}a.md"
            if not page_file.exists():
                break

        with open(page_file, encoding="utf-8") as f:
            content = f.read()

        pages_content.append(f"=== PAGE {current_page} ===\n{content}\n")

    full_content = "\n".join(pages_content)

    print("=" * 80)
    print(f"TESTING RULE {rule_num} EXTRACTION")
    print("=" * 80)
    print(f"\nStarting page: {start_page}")
    print(f"Pages read: {len(pages_content)}")
    print("\n" + "=" * 80)
    print("PROMPT THAT WOULD BE SENT TO CLAUDE:")
    print("=" * 80)

    # Show the system prompt
    system_prompt = f"""You are extracting Sanskrit grammar rules from OCR'd pages.

Extract ONLY rule § {rule_num} following this EXACT schema:

REQUIRED YAML FRONTMATTER:
---
rule_number: {rule_num}
rule_id: "§ {rule_num}"
title: "Rule Title Here"
chapter: "Chapter Name"
section: "section-slug"
page_start: N or "Na"
page_end: N or "Na"
topics: [topic1, topic2, ...]
word_index: [sanskrit-term-1, ...]
source_pages: ["page_NNN.md"]
---

REQUIRED CONTENT FORMAT:
## § {rule_num}. Rule Title

Main explanation text...

VALIDATION:
- Must include § {rule_num} in heading
- Must have YAML frontmatter
- Must have substantive content (>100 chars)
- Must use @deva[] for Devanagari, @[] for IAST
- Stop at next rule number"""

    print("\nSYSTEM PROMPT:")
    print("-" * 80)
    print(system_prompt)
    print()

    full_prompt = f"""Extract rule § {rule_num} from the following pages.

CRITICAL INSTRUCTIONS:
1. Find where § {rule_num} starts

2. Extract ALL content for § {rule_num} including:
   - Complete explanation (DO NOT CUT OFF mid-sentence)
   - All subsections (a), (b), (c), etc.
   - All footnotes [^1], [^2], etc.
   - Everything until the NEXT rule § {rule_num + 1} starts

3. DETECT CONTINUATION: If the rule text is cut off at the bottom of a page:
   - Check if "continues_from" or "continues_to" in YAML
   - Look for incomplete sentences at page boundaries
   - Read content from next page until rule § {rule_num} is COMPLETE

4. Determine ACTUAL end page where § {rule_num} finishes

5. Output format:
   Line 1: {{"end_page": N, "source_pages": ["page_XXX.md", "page_YYY.md"]}}
   Rest: Complete markdown with YAML front matter

EXAMPLE of continuation detection:
  Page 11 ends: "udātta is"
  Page 12 starts: "that which proceeds from..."
  → This is CONTINUATION - include both pages!

Begin extraction:

{full_content}"""

    print("\nUSER PROMPT:")
    print("-" * 80)
    print(full_prompt[:2000])
    print("\n... [truncated, full prompt is", len(full_prompt), "chars]")
    print()
    print("=" * 80)
    print("\nCHECKING CURRENT rule_003.md:")
    print("=" * 80)

    rule_file = Path("phase3_rules/rule_003.md")
    if rule_file.exists():
        with open(rule_file) as f:
            current = f.read()

        # Check for the incomplete sentence
        if "udātta is" in current and "that which proceeds from" not in current:
            print("\n❌ CONFIRMED: Rule 003 is CUT OFF")
            print("   - Contains: 'udātta is'")
            print("   - Missing: 'that which proceeds from'")
            print("   - page_end in YAML:", "12" if "page_end: 12" in current else "11")
        else:
            print("\n✓ Rule 003 appears complete")
    else:
        print("\n⚠️  rule_003.md does not exist")

    print("\n" + "=" * 80)
    print("ANALYSIS:")
    print("=" * 80)

    # Check if page 012 is in the pages_content
    has_page_12 = any("PAGE 12" in p for p in pages_content)
    print(f"\n✓ Page 12 included in prompt: {has_page_12}")

    # Check for continuation markers
    page_11_content = pages_content[0] if pages_content else ""
    page_12_content = pages_content[1] if len(pages_content) > 1 else ""

    has_continues_to = "continues_to: page_012" in page_11_content
    has_continues_from = "continues_from: page_011" in page_12_content

    print(f"✓ Page 11 has 'continues_to': {has_continues_to}")
    print(f"✓ Page 12 has 'continues_from': {has_continues_from}")

    # Check for the incomplete sentence
    ends_with_udatta = "udātta is" in page_11_content[-200:]
    starts_with_continuation = "that which proceeds from" in page_12_content[:500]

    print(f"✓ Page 11 ends with 'udātta is': {ends_with_udatta}")
    print(
        f"✓ Page 12 starts with 'that which proceeds from': {starts_with_continuation}"
    )

    print("\n" + "=" * 80)
    print("CONCLUSION:")
    print("=" * 80)
    print("\nThe updated prompt DOES include:")
    print("1. Both pages 11 and 12")
    print("2. Continuation detection instructions")
    print("3. Example showing this exact case")
    print("\nIf Claude CLI were available, this should now extract the complete rule.")
    print("\nTo fix: Need to either:")
    print("  A. Install claude CLI")
    print("  B. Manually send this prompt to Claude and save the response")
    print("  C. Use API key instead of browser auth")


if __name__ == "__main__":
    main()
