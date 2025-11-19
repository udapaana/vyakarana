#!/usr/bin/env python3
"""
Build Enhanced Table of Contents with Hierarchical Structure
Groups rules by chapter and identifies subsections based on topics
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict, OrderedDict

CORE_CLEANED = Path("phase3_rules/core/cleaned")
APPENDIX_CLEANED = Path("phase3_rules/appendix_prosody/cleaned")

def read_rule_metadata(file_path: Path) -> Dict:
    """Extract frontmatter metadata from a rule file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract YAML frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                metadata = yaml.safe_load(parts[1])
                return metadata
            except yaml.YAMLError as e:
                print(f"Error parsing {file_path}: {e}")
                return {}
    return {}

def build_toc_data():
    """Build hierarchical TOC data structure from all rules."""
    all_rules = []

    # Process core rules
    for i in range(1, 973):
        if i < 100:
            file_path = CORE_CLEANED / f"rule_{i:03d}.md"
        else:
            file_path = CORE_CLEANED / f"rule_{i}.md"

        if file_path.exists():
            metadata = read_rule_metadata(file_path)
            if metadata:
                metadata['type'] = 'core'
                metadata['file_path'] = str(file_path)
                all_rules.append(metadata)

    # Process appendix prosody rules
    for i in range(1, 15):
        file_path = APPENDIX_CLEANED / f"rule_{i:03d}.md"

        if file_path.exists():
            metadata = read_rule_metadata(file_path)
            if metadata:
                metadata['type'] = 'appendix'
                metadata['file_path'] = str(file_path)
                all_rules.append(metadata)

    return all_rules

def get_chapter_order():
    """Define the standard chapter order from the book."""
    return [
        ("I", "The Alphabet", 1, 34),
        ("II", "Euphonic Combination of Letters (Sandhi)", 35, 71),
        ("III", "Declension of Nouns", 73, 178),
        ("IV", "Formation of Feminine Bases", 179, 336),  # Actually starts at 305
        ("V", "Pronouns and Their Declension", 196, 221),
        ("VI", "Numerals and Their Declension", 222, 241),
        ("VII", "Compounds", 242, 304),  # Actually includes 179-304
        ("VIII", "Conjugation of Verbs", 337, 487),  # Includes secondary conjugations
        ("IX", "Formation of Nouns from Verbs and Nouns", 488, 603),
        ("X", "Indeclinables (Avyayas)", 363, 377),  # Embedded in VIII
        ("XI", "Formation of Nouns by Kṛit Affixes", 501, 603),
        ("XII", "Formation of Participles and Gerunds", 604, 683),
        ("XIII", "Accents", 630, 672),  # Embedded in XII
        ("XIV", "Vedic Grammar", 673, 807),
        ("XV", "Syntax", 808, 972),
        ("Appendix I", "Prosody", 1, 14),
    ]

def group_rules_by_chapter(rules: List[Dict]) -> OrderedDict:
    """Group rules by their chapter field."""
    chapters = OrderedDict()

    for rule in rules:
        chapter = rule.get('chapter', 'Unknown')
        if chapter not in chapters:
            chapters[chapter] = []
        chapters[chapter].append(rule)

    return chapters

def identify_subsections(rules: List[Dict]) -> List[Tuple[str, List[Dict]]]:
    """Identify natural subsections within a list of rules based on topics."""
    subsections = []
    current_subsection_name = None
    current_subsection_rules = []

    for rule in rules:
        title = rule.get('title', '')
        topics = rule.get('topics', [])
        rule_num = rule.get('rule_number', 0)

        # Detect subsection boundaries based on title patterns and topic shifts
        # This is a heuristic approach
        new_subsection = None

        # Check for major topic changes
        if rule_num == rules[0].get('rule_number'):  # First rule
            new_subsection = "Introduction and Fundamentals"
        elif "Introduction" in title or "Definition" in title or title.startswith("Vṛitti:") or title.startswith("Samāsas:"):
            new_subsection = "Definitions and Principles"
        elif rule == rules[0]:
            new_subsection = "General Rules"

        if new_subsection:
            if current_subsection_rules:
                subsections.append((current_subsection_name, current_subsection_rules))
            current_subsection_name = new_subsection
            current_subsection_rules = [rule]
        else:
            if current_subsection_rules:
                current_subsection_rules.append(rule)
            else:
                current_subsection_name = "General Rules"
                current_subsection_rules = [rule]

    # Add the last subsection
    if current_subsection_rules:
        subsections.append((current_subsection_name, current_subsection_rules))

    # If no subsections identified, return all as one section
    if not subsections:
        subsections = [("All Rules", rules)]

    return subsections

def format_rule_entry(rule: Dict, indent: int = 0) -> str:
    """Format a single rule entry for the TOC."""
    rule_id = rule.get('rule_id', '')
    rule_num = rule.get('rule_number', '')
    title = rule.get('title', '')
    page = rule.get('page_start', '')
    topics = rule.get('topics', [])

    # Create indentation
    prefix = "  " * indent

    # Format the line
    line = f"{prefix}- **{rule_id}**: {title}"

    # Add page reference
    if page:
        line += f" (p. {page})"

    # Optionally add key topics in subtle way
    if topics and len(topics) <= 3:
        topic_str = ", ".join(topics[:3])
        # line += f" *[{topic_str}]*"

    return line

def generate_enhanced_toc_markdown(all_rules: List[Dict]) -> str:
    """Generate enhanced markdown table of contents with hierarchy."""
    lines = []

    # Header
    lines.append("# Kale's Higher Sanskrit Grammar")
    lines.append("# Complete Hierarchical Table of Contents")
    lines.append("")
    lines.append("**Edition:** 7th Edition (1931)")
    lines.append("**Author:** M.R. Kale")
    lines.append("**Total Rules:** 986 (972 core + 14 appendix prosody)")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Table of Contents Overview")
    lines.append("")

    # Group rules by chapter
    chapters = group_rules_by_chapter(all_rules)

    # Generate quick navigation links
    chapter_num = 1
    for chapter_name, chapter_rules in chapters.items():
        if chapter_name != "Unknown":
            # Determine if it's appendix
            if "Appendix" in chapter_name or "Prosody" in chapter_name:
                lines.append(f"- [Appendix I: {chapter_name}](#{chapter_name.lower().replace(' ', '-').replace(':', '').replace('(', '').replace(')', '')}) — {len(chapter_rules)} rules")
            else:
                # Try to match with standard chapter numbers
                roman_nums = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV', 'XV']
                if chapter_num <= len(roman_nums):
                    chapter_marker = f"Chapter {roman_nums[chapter_num - 1]}"
                else:
                    chapter_marker = f"Chapter"

                lines.append(f"- [{chapter_marker}: {chapter_name}](#{chapter_name.lower().replace(' ', '-').replace(':', '').replace('(', '').replace(')', '')}) — {len(chapter_rules)} rules")
                chapter_num += 1

    lines.append("")
    lines.append("---")
    lines.append("")

    # Generate detailed TOC
    chapter_counter = 1
    for chapter_name, chapter_rules in chapters.items():
        if chapter_name == "Unknown":
            continue

        # Sort rules by rule number
        chapter_rules.sort(key=lambda r: r.get('rule_number', 0))

        # Determine chapter number
        if "Appendix" in chapter_name or "Prosody" in chapter_name:
            chapter_header = f"## Appendix I: Prosody"
        else:
            roman_nums = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV', 'XV']
            if chapter_counter <= len(roman_nums):
                chapter_header = f"## Chapter {roman_nums[chapter_counter - 1]}: {chapter_name}"
            else:
                chapter_header = f"## {chapter_name}"
            chapter_counter += 1

        lines.append(chapter_header)
        lines.append("")

        # Chapter info
        first_rule = chapter_rules[0].get('rule_number', '?')
        last_rule = chapter_rules[-1].get('rule_number', '?')
        lines.append(f"**Rule Range:** § {first_rule}—{last_rule}")
        lines.append(f"**Total Rules:** {len(chapter_rules)}")
        lines.append("")

        # List all rules
        for rule in chapter_rules:
            lines.append(format_rule_entry(rule))

        lines.append("")
        lines.append("---")
        lines.append("")

    # Summary statistics
    lines.append("## Summary Statistics")
    lines.append("")
    lines.append(f"- **Total Chapters:** {len([c for c in chapters.keys() if c != 'Unknown'])} (15 main + 1 appendix)")
    lines.append(f"- **Total Rules:** {len(all_rules)}")

    core_rules = [r for r in all_rules if r.get('type') == 'core']
    appendix_rules = [r for r in all_rules if r.get('type') == 'appendix']

    lines.append(f"  - Core Grammar: {len(core_rules)} rules (§ 1—972)")
    lines.append(f"  - Appendix Prosody: {len(appendix_rules)} rules (§ 1—14)")
    lines.append("")
    lines.append("### Chapter Distribution")
    lines.append("")

    for chapter_name, chapter_rules in chapters.items():
        if chapter_name != "Unknown":
            lines.append(f"- **{chapter_name}**: {len(chapter_rules)} rules")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Generated from production-ready rule metadata (Phase 3C)*")
    lines.append("")

    return "\n".join(lines)

def main():
    print("Building Enhanced Hierarchical Table of Contents...")
    print("=" * 70)

    # Build TOC data
    all_rules = build_toc_data()

    print(f"\nTotal rules loaded: {len(all_rules)}")

    # Group by chapter
    chapters = group_rules_by_chapter(all_rules)

    print(f"Chapters identified: {len(chapters)}")
    for chapter, rules in chapters.items():
        print(f"  - {chapter}: {len(rules)} rules")

    # Generate enhanced markdown
    markdown = generate_enhanced_toc_markdown(all_rules)

    # Write to file
    output_file = Path("TABLE_OF_CONTENTS.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"\n✅ Enhanced Table of Contents written to: {output_file}")
    print(f"   Total rules: {len(all_rules)}")
    print(f"   Total chapters: {len([c for c in chapters.keys() if c != 'Unknown'])}")
    print("=" * 70)

if __name__ == "__main__":
    main()
