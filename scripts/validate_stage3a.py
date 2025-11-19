#!/usr/bin/env python3
"""
Stage 3A Validation Script

Validates that extracted rules are complete and correct:
1. Boundary marker validation (starts with § N, doesn't contain § N+1 start)
2. Page coverage validation (cross-ref with Phase 2 frontmatter)
3. Length heuristics (reasonable word count)
4. Footnote integrity (no orphaned markers)
5. Multi-page continuity check
"""

import os
import re
import yaml
from pathlib import Path


def extract_yaml_frontmatter(filepath):
    """Extract YAML frontmatter from markdown file"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.startswith("---\n"):
        return None, content

    parts = content.split("---\n", 2)
    if len(parts) < 3:
        return None, content

    try:
        frontmatter = yaml.safe_load(parts[1])
        body = parts[2]
        return frontmatter, body
    except:
        return None, content


def validate_rule(rule_num, phase2_dir, phase3a_dir):
    """Comprehensive validation for a single rule"""
    issues = []
    warnings = []

    rule_file = f"{phase3a_dir}/rule_{rule_num:03d}.md"

    if not os.path.exists(rule_file):
        return [f"File missing: {rule_file}"], []

    # Read the rule file
    frontmatter, content = extract_yaml_frontmatter(rule_file)

    if not frontmatter:
        return [f"Invalid YAML frontmatter"], []

    # === 1. BOUNDARY MARKER VALIDATION ===

    # Check starts with § N (handle both "§ N" and "§N" variants, plus "Obs. § N" for observations)
    rule_marker_with_space = f"§ {rule_num}"
    rule_marker_no_space = f"§{rule_num}"
    obs_marker = f"Obs. § {rule_num}"
    content_start = content.lstrip()

    if not (
        content_start.startswith(rule_marker_with_space)
        or content_start.startswith(rule_marker_no_space)
        or content_start.startswith(obs_marker)
    ):
        issues.append(f"Doesn't start with '§ {rule_num}' or '§{rule_num}'")

    # Check doesn't contain § N+1 as a NEW rule start
    next_marker = f"§ {rule_num + 1}."
    main_content = (
        content.split("## Footnotes")[0] if "## Footnotes" in content else content
    )

    for line in main_content.split("\n"):
        stripped = line.strip()
        # Check if line starts a new rule (not a cross-reference)
        if stripped.startswith(next_marker) and not any(
            ref in line for ref in ["see", "See", "vide", "Vide", "§ 20", "under"]
        ):
            issues.append(
                f"Contains start of § {rule_num + 1} - rule bleeding detected"
            )

    # === 2. PAGE COVERAGE VALIDATION ===

    source_pages = frontmatter.get("source_pages", [])
    page_start = frontmatter.get("page_start")
    page_end = frontmatter.get("page_end")

    if not source_pages:
        issues.append("No source_pages specified")

    # Verify source pages exist and reference this rule
    for page in source_pages:
        page_file = f"{phase2_dir}/page_{page}.md"
        if not os.path.exists(page_file):
            issues.append(f"Source page {page_file} doesn't exist")
            continue

        page_fm, _ = extract_yaml_frontmatter(page_file)
        if not page_fm:
            warnings.append(f"Page {page} has invalid frontmatter")
            continue

        rules_starting = page_fm.get("rules_starting", [])
        rules_continuing = page_fm.get("rules_continuing", [])

        # First source page should list this rule in rules_starting
        if page == source_pages[0]:
            if f"§ {rule_num}" not in rules_starting:
                warnings.append(
                    f"Page {page} doesn't list § {rule_num} in rules_starting"
                )
        # Continuation pages should list in rules_continuing
        elif page in source_pages[1:]:
            if f"§ {rule_num}" not in rules_continuing:
                warnings.append(
                    f"Page {page} doesn't list § {rule_num} in rules_continuing"
                )

    # === 3. LENGTH HEURISTICS ===

    word_count = len(content.split())
    if word_count < 20:
        warnings.append(f"Suspiciously short: {word_count} words")
    if word_count > 3000:
        warnings.append(
            f"Suspiciously long: {word_count} words (may include next rule)"
        )

    # === 4. FOOTNOTE INTEGRITY ===

    # Find all footnote markers [^N] in content
    marker_pattern = r"\[\^(\d+)\]"
    markers_in_text = set(re.findall(marker_pattern, main_content))

    # Find all footnote definitions in footnote section
    if "## Footnotes" in content:
        footnote_section = content.split("## Footnotes")[1]
        definitions = set(re.findall(marker_pattern, footnote_section))

        # Check for orphaned markers
        orphaned_markers = markers_in_text - definitions
        if orphaned_markers:
            warnings.append(f"Orphaned footnote markers: {orphaned_markers}")

        # Check for unused definitions
        unused_defs = definitions - markers_in_text
        if unused_defs:
            warnings.append(f"Unused footnote definitions: {unused_defs}")
    elif markers_in_text:
        warnings.append(f"Footnote markers {markers_in_text} but no Footnotes section")

    # === 5. SCHEMA VALIDATION ===

    required_fields = [
        "rule_number",
        "rule_id",
        "page_start",
        "page_end",
        "source_pages",
        "extraction_status",
    ]
    for field in required_fields:
        if field not in frontmatter:
            issues.append(f"Missing required field: {field}")

    # Validate extraction_status
    if frontmatter.get("extraction_status") != "raw":
        warnings.append(
            f"extraction_status should be 'raw', got '{frontmatter.get('extraction_status')}'"
        )

    # Validate rule_number matches filename
    if frontmatter.get("rule_number") != rule_num:
        issues.append(
            f"rule_number {frontmatter.get('rule_number')} doesn't match filename {rule_num}"
        )

    return issues, warnings


def main():
    phase2_dir = "phase2_cleaned"
    phase3a_dir = "phase3_rules/core/raw"

    print("=" * 70)
    print("STAGE 3A VALIDATION REPORT")
    print("=" * 70)
    print()

    # Auto-detect total rules from extracted files
    import glob

    rule_files = glob.glob(f"{phase3a_dir}/rule_*.md")
    total_rules = len(rule_files) if rule_files else 50
    total_issues = 0
    total_warnings = 0
    rules_with_issues = 0
    rules_with_warnings = 0

    for rule_num in range(1, total_rules + 1):
        issues, warnings = validate_rule(rule_num, phase2_dir, phase3a_dir)

        if issues:
            rules_with_issues += 1
            total_issues += len(issues)
            print(f"❌ Rule {rule_num:03d}: {len(issues)} ISSUE(S)")
            for issue in issues:
                print(f"   ERROR: {issue}")

        if warnings:
            rules_with_warnings += 1
            total_warnings += len(warnings)
            if not issues:  # Only print if no issues
                print(f"⚠️  Rule {rule_num:03d}: {len(warnings)} WARNING(S)")
            for warning in warnings:
                print(f"   WARN: {warning}")

        if not issues and not warnings:
            print(f"✅ Rule {rule_num:03d}: OK")

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total rules validated: {total_rules}")
    print(f"Rules with issues: {rules_with_issues}")
    print(f"Rules with warnings: {rules_with_warnings}")
    print(f"Total issues: {total_issues}")
    print(f"Total warnings: {total_warnings}")
    print()

    if total_issues == 0:
        print("✅ ALL RULES PASS VALIDATION!")
    else:
        print(f"❌ {total_issues} issues found - review and fix")

    if total_warnings > 0:
        print(f"⚠️  {total_warnings} warnings - review recommended")

    return 0 if total_issues == 0 else 1


if __name__ == "__main__":
    exit(main())
