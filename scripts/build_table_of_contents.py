#!/usr/bin/env python3
"""
Build Comprehensive Table of Contents from Rule Metadata
Analyzes all 986 rules to extract chapter, section, and title information
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

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
    """Build TOC data structure from all rules."""
    toc = defaultdict(list)

    # Process core rules
    for i in range(1, 973):
        if i < 100:
            file_path = CORE_CLEANED / f"rule_{i:03d}.md"
        else:
            file_path = CORE_CLEANED / f"rule_{i}.md"

        if file_path.exists():
            metadata = read_rule_metadata(file_path)
            if metadata:
                chapter = metadata.get('chapter', 'Unknown')
                entry = {
                    'rule_id': metadata.get('rule_id', f'§ {i}'),
                    'rule_number': metadata.get('rule_number', i),
                    'title': metadata.get('title', ''),
                    'section': metadata.get('section', ''),
                    'page_start': metadata.get('page_start', ''),
                }
                toc[chapter].append(entry)

    # Process appendix prosody rules
    appendix_rules = []
    for i in range(1, 15):
        file_path = APPENDIX_CLEANED / f"rule_{i:03d}.md"

        if file_path.exists():
            metadata = read_rule_metadata(file_path)
            if metadata:
                entry = {
                    'rule_id': metadata.get('rule_id', f'§ {i}'),
                    'rule_number': metadata.get('rule_number', i),
                    'title': metadata.get('title', ''),
                    'section': metadata.get('section', ''),
                    'page_start': metadata.get('page_start', ''),
                }
                appendix_rules.append(entry)

    if appendix_rules:
        toc['Appendix I: Prosody'] = appendix_rules

    return dict(toc)

def generate_toc_markdown(toc_data: Dict) -> str:
    """Generate markdown table of contents."""
    lines = []
    lines.append("# Kale's Higher Sanskrit Grammar - Complete Table of Contents")
    lines.append("")
    lines.append("**Edition:** 7th Edition (1931)")
    lines.append("**Author:** M.R. Kale")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Define chapter order from the book
    chapter_order = [
        "The Alphabet",
        "Euphonic Combination of Letters (Sandhi)",
        "Declension",
        "Formation of Feminine Bases",
        "Pronouns",
        "Numerals",
        "Compounds",
        "Conjugation of Verbs",
        "Formation of Nouns from Verbs and Nouns",
        "Indeclinables (Avyayas)",
        "Formation of Nouns by Kṛit Affixes",
        "Formation of Participles and Gerunds",
        "Accents",
        "Vedic Grammar",
        "Syntax",
        "Appendix I: Prosody",
    ]

    # Process each chapter
    for chapter_name in chapter_order:
        if chapter_name in toc_data:
            rules = toc_data[chapter_name]

            # Chapter header
            lines.append(f"## {chapter_name}")
            lines.append("")
            lines.append(f"**Total Rules:** {len(rules)}")
            lines.append("")

            # Rules list
            for rule in rules:
                rule_id = rule['rule_id']
                title = rule['title']
                page = rule.get('page_start', '')

                # Format as: § N: Title (page X)
                line = f"- **{rule_id}**: {title}"
                if page:
                    line += f" (p. {page})"
                lines.append(line)

            lines.append("")
            lines.append("---")
            lines.append("")

    # Summary statistics
    total_rules = sum(len(rules) for rules in toc_data.values())
    lines.append("## Summary Statistics")
    lines.append("")
    lines.append(f"- **Total Chapters:** {len(toc_data)}")
    lines.append(f"- **Total Rules:** {total_rules}")
    lines.append("  - Core Grammar Rules: 972 (§ 1-972)")
    lines.append("  - Appendix Prosody: 14 (§ 1-14)")
    lines.append("")

    return "\n".join(lines)

def main():
    print("Building Table of Contents from rule metadata...")
    print("=" * 70)

    # Build TOC data
    toc_data = build_toc_data()

    print(f"\nChapters found: {len(toc_data)}")
    for chapter, rules in toc_data.items():
        print(f"  - {chapter}: {len(rules)} rules")

    # Generate markdown
    markdown = generate_toc_markdown(toc_data)

    # Write to file
    output_file = Path("TABLE_OF_CONTENTS.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"\n✅ Table of Contents written to: {output_file}")
    print(f"   Total rules processed: {sum(len(rules) for rules in toc_data.values())}")
    print("=" * 70)

if __name__ == "__main__":
    main()
