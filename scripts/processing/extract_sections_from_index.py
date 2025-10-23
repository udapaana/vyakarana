#!/usr/bin/env python3
"""
Extract sections from v7 using the AI-generated index

Uses sections_index.json to extract each rule into its own file
with nested folder structure capturing document hierarchy.
"""

import json
import yaml
import re
from pathlib import Path
from typing import Dict, List

def slugify(text: str) -> str:
    """Convert text to filesystem-safe slug"""
    # Remove Sanskrit tags
    text = re.sub(r'@\[([^\]]+)\]', r'\1', text)
    # Convert to lowercase
    slug = text.lower()
    # Replace non-alphanumeric with underscore
    slug = re.sub(r'[^a-z0-9]+', '_', slug)
    # Remove leading/trailing underscores
    slug = slug.strip('_')
    # Limit length
    if len(slug) > 50:
        slug = slug[:50].rstrip('_')
    return slug

def roman_to_int(roman: str) -> int:
    """Convert roman numeral to integer"""
    roman_map = {
        'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
        'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10,
        'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15,
        'XVI': 16, 'XVII': 17, 'XVIII': 18, 'XIX': 19, 'XX': 20
    }
    return roman_map.get(roman, 0)

def extract_rule_content(lines: List[str], start_line: int, end_line: int) -> List[str]:
    """Extract content for a rule between start and end lines"""
    # Lines are 1-indexed in the index, but 0-indexed in the list
    content = []

    first_line = True

    for i in range(start_line - 1, end_line):
        if i < len(lines):
            line = lines[i]

            # If this is the first line with #### § N., strip the header but keep the content after it
            if first_line and line.strip().startswith('#### §'):
                first_line = False
                match = re.match(r'^####\s*§\s*\d+\.\s*(.*)', line)
                if match and match.group(1).strip():
                    # There's content after the § marker - keep it
                    content.append(match.group(1) + '\n')
                continue

            # Stop if we hit ANY markdown header (next rule, subsection, etc.)
            if line.strip().startswith('#'):
                break

            content.append(line)
    return content

def create_rule_file(base_dir: Path, chapter_num: int, chapter_slug: str,
                     section_num: int, section_slug: str,
                     rule: Dict, content: List[str]):
    """Create a single rule file with front matter in nested directory structure"""

    # Create nested directory structure: chapter/section/
    chapter_dir = f"{chapter_num:02d}_{chapter_slug}"
    section_dir = f"{section_num:02d}_{section_slug}"

    dir_path = base_dir / chapter_dir / section_dir
    dir_path.mkdir(parents=True, exist_ok=True)

    # Create filename
    rule_num = int(rule['number'])
    file_path = dir_path / f"s{rule_num:03d}.md"

    # Build front matter - minimal structural metadata only
    frontmatter = {
        'rule': f"§{rule['number']}"
    }

    # Write file
    with open(file_path, 'w', encoding='utf-8') as f:
        # Write front matter
        f.write('---\n')
        f.write(yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True))
        f.write('---\n\n')

        # Write content
        f.writelines(content)

    return file_path

def main():
    project_root = Path(__file__).parent.parent.parent
    v7_file = project_root / "output" / "kales_sanskrit_grammar_v7.md"
    index_file = project_root / "sections_index.json"
    output_dir = project_root / "v8_sections"

    if not v7_file.exists():
        print(f"❌ Error: v7 file not found at {v7_file}")
        return

    if not index_file.exists():
        print(f"❌ Error: index file not found at {index_file}")
        print(f"   Run identify_sections_ai.py first")
        return

    # Load v7 content
    print(f"📖 Loading v7: {v7_file}")
    with open(v7_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    print(f"   Loaded {len(lines)} lines")

    # Load index
    print(f"📑 Loading index: {index_file}")
    with open(index_file, 'r', encoding='utf-8') as f:
        index = json.load(f)

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    print(f"\n🔨 Extracting sections...")
    print(f"   Output: {output_dir}/\n")

    files_created = 0
    total_rules = 0

    # Process each chapter
    for chapter in index['chapters']:
        chapter_num = roman_to_int(chapter['number'])
        chapter_slug = f"chapter_{chapter['number'].lower()}"

        print(f"\n📂 Chapter {chapter['number']} → {chapter_num:02d}_{chapter_slug}/")

        # Process each section in this chapter
        sections = chapter.get('sections', [])
        for section_idx, section in enumerate(sections, 1):
            section_title = section['title']
            section_slug = slugify(section_title)

            rules = section.get('rules', [])
            if not rules:
                continue

            print(f"   📁 {section_idx:02d}. {section_title[:60]}... ({len(rules)} rules)")

            # Process each rule
            for i, rule in enumerate(rules):
                # Determine end line (start of next rule or end of section)
                if i + 1 < len(rules):
                    # Next rule exists - go until that
                    end_line = rules[i + 1]['start_line']
                else:
                    # Last rule in this section - find next section or chapter boundary
                    # Look ahead to find next section in this chapter
                    next_section_line = None
                    for next_sec_idx in range(section_idx, len(sections)):
                        if next_sec_idx > section_idx - 1:
                            next_section_line = sections[next_sec_idx]['start_line']
                            break

                    # If no next section, check for next chapter
                    if not next_section_line:
                        # Find this chapter's index and look for next chapter
                        for chap_idx, chap in enumerate(index['chapters']):
                            if chap['number'] == chapter['number'] and chap_idx + 1 < len(index['chapters']):
                                next_section_line = index['chapters'][chap_idx + 1]['start_line']
                                break

                    # If still nothing, use end of document
                    end_line = next_section_line if next_section_line else len(lines)

                # Extract content
                content = extract_rule_content(lines, rule['start_line'], end_line)

                # Create file
                file_path = create_rule_file(
                    output_dir,
                    chapter_num,
                    chapter_slug,
                    section_idx,
                    section_slug,
                    rule,
                    content
                )

                files_created += 1
                total_rules += 1

                if int(rule['number']) % 50 == 0:  # Print every 50th
                    rel_path = file_path.relative_to(output_dir)
                    print(f"      ✅ §{rule['number']}: {rel_path}")

    print(f"\n✅ Extraction complete!")
    print(f"   Files created: {files_created}")
    print(f"   Total rules: {total_rules}")
    print(f"   Output directory: {output_dir}/")

    # Print summary with better structure
    print(f"\n📊 Directory Structure:")

    for chapter_dir in sorted(output_dir.iterdir()):
        if not chapter_dir.is_dir():
            continue

        # Count all files in this chapter
        total_files = len(list(chapter_dir.rglob("*.md")))
        section_count = len([d for d in chapter_dir.iterdir() if d.is_dir()])

        print(f"\n   {chapter_dir.name}/ ({section_count} sections, {total_files} files)")

        # Show sections
        for section_dir in sorted(chapter_dir.iterdir()):
            if section_dir.is_dir():
                section_files = list(section_dir.glob("*.md"))
                if section_files:
                    # Get rule number range
                    rule_nums = sorted([int(f.stem[1:]) for f in section_files])
                    range_str = f"§{rule_nums[0]}-§{rule_nums[-1]}" if len(rule_nums) > 1 else f"§{rule_nums[0]}"
                    print(f"      {section_dir.name}/ ({len(section_files)} files: {range_str})")

if __name__ == "__main__":
    main()
