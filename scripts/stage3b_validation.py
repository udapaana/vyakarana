#!/usr/bin/env python3
"""
Stage 3B: Validation - Verify all structured rules meet schema requirements
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path("/Users/skmnktl/Downloads/ocr")
STRUCTURED_DIR = BASE_DIR / "phase3_rules/core/structured"


def validate_rule(rule_num: int) -> Dict:
    """Validate a single structured rule file"""
    file_path = STRUCTURED_DIR / f"rule_{rule_num:03d}.md"

    result = {
        "rule_num": rule_num,
        "valid": False,
        "errors": [],
        "warnings": [],
        "stats": {},
    }

    if not file_path.exists():
        result["errors"].append("File not found")
        return result

    try:
        content = file_path.read_text(encoding="utf-8")

        # Split frontmatter and body
        parts = content.split("---", 2)
        if len(parts) < 3:
            result["errors"].append("Invalid frontmatter structure")
            return result

        yaml_text = parts[1].strip()
        body = parts[2].strip()

        # Parse YAML
        try:
            metadata = yaml.safe_load(yaml_text)
        except yaml.YAMLError as e:
            result["errors"].append(f"YAML parse error: {e}")
            return result

        # Required fields validation
        required_fields = [
            "rule_number",
            "rule_id",
            "title",
            "chapter",
            "section",
            "page_start",
            "page_end",
            "topics",
            "word_index",
            "panini_refs",
            "cross_refs",
            "source_pages",
            "extraction_status",
        ]

        for field in required_fields:
            if field not in metadata:
                result["errors"].append(f"Missing required field: {field}")

        # Field value validation
        if metadata.get("rule_number") != rule_num:
            result["errors"].append(
                f"Rule number mismatch: {metadata.get('rule_number')} != {rule_num}"
            )

        if metadata.get("rule_id") != f"§ {rule_num}":
            result["errors"].append(f"Rule ID mismatch: {metadata.get('rule_id')}")

        if not metadata.get("title"):
            result["errors"].append("Title is empty")

        if metadata.get("extraction_status") != "structured":
            result["errors"].append(
                f"Wrong extraction status: {metadata.get('extraction_status')}"
            )

        # Chapter/section validation
        chapter = metadata.get("chapter", "")
        section = metadata.get("section", "")

        if 1 <= rule_num <= 17:
            if chapter != "The Alphabet":
                result["errors"].append(
                    f"Wrong chapter: {chapter} (expected 'The Alphabet')"
                )
            if section != "alphabet":
                result["errors"].append(
                    f"Wrong section: {section} (expected 'alphabet')"
                )
        elif 18 <= rule_num <= 50:
            if chapter != "Rules of Sandhi":
                result["errors"].append(
                    f"Wrong chapter: {chapter} (expected 'Rules of Sandhi')"
                )
            if section != "sandhi":
                result["errors"].append(f"Wrong section: {section} (expected 'sandhi')")

        # Topics validation
        topics = metadata.get("topics", [])
        if not topics:
            result["warnings"].append("No topics specified")
        elif len(topics) < 2:
            result["warnings"].append(
                f"Only {len(topics)} topic(s) - consider adding more"
            )

        # Content validation
        if len(body) < 100:
            result["warnings"].append(f"Content seems short ({len(body)} chars)")

        # Check for markdown heading
        if not re.search(r"^## .+$", body, re.MULTILINE):
            result["errors"].append("Missing markdown heading (## Title)")

        # Check title matches
        title_in_yaml = metadata.get("title", "")
        heading_match = re.search(r"^## (.+)$", body, re.MULTILINE)
        if heading_match:
            title_in_heading = heading_match.group(1).strip()
            if title_in_yaml != title_in_heading:
                result["errors"].append(f"Title mismatch: YAML vs heading")

        # Check for footnotes consistency if present
        footnote_refs = re.findall(r"\[\^(\d+)\]", body)
        footnote_defs = re.findall(r"^\[\^(\d+)\]:", body, re.MULTILINE)

        if footnote_refs:
            unique_refs = sorted(set(footnote_refs), key=int)
            unique_defs = sorted(set(footnote_defs), key=int)

            if unique_refs != unique_defs:
                result["warnings"].append(
                    f"Footnote mismatch: refs={unique_refs}, defs={unique_defs}"
                )

        # Stats
        result["stats"] = {
            "title": metadata.get("title", ""),
            "chapter": chapter,
            "topics_count": len(topics),
            "word_index_count": len(metadata.get("word_index", [])),
            "panini_refs_count": len(metadata.get("panini_refs", [])),
            "cross_refs_count": len(metadata.get("cross_refs", [])),
            "content_length": len(body),
            "devanagari_terms": len(re.findall(r"[\u0900-\u097F]+", body)),
        }

        # Mark as valid if no errors
        if not result["errors"]:
            result["valid"] = True

    except Exception as e:
        result["errors"].append(f"Exception: {str(e)}")

    return result


def main():
    """Validate all structured rules 1-50"""
    print("Stage 3B: Validating Structured Rules 1-50")
    print("=" * 70)

    results = []
    valid_count = 0
    error_count = 0
    warning_count = 0

    for rule_num in range(1, 51):
        result = validate_rule(rule_num)
        results.append(result)

        if result["valid"]:
            valid_count += 1
            status = "✓"
        else:
            error_count += 1
            status = "✗"

        if result["warnings"]:
            warning_count += 1

        # Print compact status
        title = result["stats"].get("title", "Unknown")[:50]
        print(f"{status} Rule {rule_num:03d}: {title}")

        # Print errors
        for error in result["errors"]:
            print(f"    ERROR: {error}")

        # Print warnings (only first one to keep output compact)
        if result["warnings"]:
            print(f"    WARNING: {result['warnings'][0]}")

    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Total rules processed: {len(results)}")
    print(f"Valid rules: {valid_count}")
    print(f"Rules with errors: {error_count}")
    print(f"Rules with warnings: {warning_count}")

    # Aggregate stats
    print("\n" + "=" * 70)
    print("AGGREGATE STATISTICS")
    print("=" * 70)

    total_topics = sum(r["stats"].get("topics_count", 0) for r in results)
    total_word_index = sum(r["stats"].get("word_index_count", 0) for r in results)
    total_panini_refs = sum(r["stats"].get("panini_refs_count", 0) for r in results)
    total_cross_refs = sum(r["stats"].get("cross_refs_count", 0) for r in results)
    total_devanagari = sum(r["stats"].get("devanagari_terms", 0) for r in results)

    print(
        f"Total topics: {total_topics} (avg: {total_topics / len(results):.1f} per rule)"
    )
    print(
        f"Total word_index entries: {total_word_index} (avg: {total_word_index / len(results):.1f} per rule)"
    )
    print(
        f"Total Pāṇini references: {total_panini_refs} (avg: {total_panini_refs / len(results):.1f} per rule)"
    )
    print(
        f"Total cross-references: {total_cross_refs} (avg: {total_cross_refs / len(results):.1f} per rule)"
    )
    print(f"Total Devanagari terms in content: {total_devanagari}")

    # Chapter breakdown
    alphabet_rules = [r for r in results if r["stats"].get("chapter") == "The Alphabet"]
    sandhi_rules = [
        r for r in results if r["stats"].get("chapter") == "Rules of Sandhi"
    ]

    print(f"\nChapter breakdown:")
    print(f"  The Alphabet: {len(alphabet_rules)} rules (§1-17)")
    print(f"  Rules of Sandhi: {len(sandhi_rules)} rules (§18-50)")

    # Sample titles
    print("\n" + "=" * 70)
    print("SAMPLE TITLES (First 10 Rules)")
    print("=" * 70)

    for i, result in enumerate(results[:10], 1):
        title = result["stats"].get("title", "Unknown")
        print(f"§ {i:2d}: {title}")

    print("\n" + "=" * 70)
    print("SAMPLE TITLES (Rules 18-27 - Sandhi Section)")
    print("=" * 70)

    for i in range(18, 28):
        result = results[i - 1]
        title = result["stats"].get("title", "Unknown")
        print(f"§ {i:2d}: {title}")

    # Issues summary
    if error_count > 0:
        print("\n" + "=" * 70)
        print("ERRORS REQUIRING ATTENTION")
        print("=" * 70)
        for result in results:
            if result["errors"]:
                print(f"\nRule {result['rule_num']:03d}:")
                for error in result["errors"]:
                    print(f"  - {error}")

    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    exit(main())
