#!/usr/bin/env python3
"""
Extract sections from v7 into individual files with front matter

Usage:
    python extract_sections.py

Input:  output/kales_sanskrit_grammar_v7.md
Output: v8_sections/{chapter}/{section}/s{num}.md

Each file gets:
- Folder structure (chapter/section hierarchy)
- Front matter (rule number, title, page)
- Content (raw from v7, to be processed by Claude)
"""

import re
import yaml
from pathlib import Path
from typing import Optional, Dict, List

class SectionExtractor:
    def __init__(self, v7_path: Path, output_dir: Path):
        self.v7_path = v7_path
        self.output_dir = output_dir
        self.content: List[str] = []
        self.current_chapter: Optional[str] = None
        self.current_section: Optional[str] = None
        self.section_counter = 0

    def load_v7(self):
        """Load v7 content"""
        print(f"📖 Loading v7: {self.v7_path}")
        with open(self.v7_path, 'r', encoding='utf-8') as f:
            self.content = f.readlines()
        print(f"   Loaded {len(self.content)} lines")

    def detect_chapter(self, line: str) -> Optional[str]:
        """Detect chapter heading"""
        # Pattern: # Chapter I. or # CHAPTER II.
        match = re.match(r'^#\s+(CHAPTER|Chapter)\s+([IVX]+|[0-9]+)\.?\s*$', line.strip())
        if match:
            num = match.group(2)
            # Convert roman to number if needed
            if num.isdigit():
                return f"{int(num):02d}"
            else:
                # Simple roman numeral conversion
                roman_map = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
                           'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10,
                           'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15}
                return f"{roman_map.get(num, 0):02d}"
        return None

    def detect_section(self, line: str) -> Optional[str]:
        """Detect section heading"""
        # Pattern: ## SECTION or ### I. SVARASANDHI
        if line.startswith('##'):
            # Extract section name, clean it
            section = line.strip('#').strip()
            # Convert to slug
            slug = section.lower()
            slug = re.sub(r'[^a-z0-9]+', '_', slug)
            slug = slug.strip('_')
            return slug
        return None

    def detect_rule(self, line: str) -> Optional[Dict[str, str]]:
        """Detect rule paragraph (§ marker)"""
        # Pattern: #### § 19. Title or just #### § 19
        match = re.match(r'^####\s*§\s*(\d+)\.\s*(.*)', line.strip())
        if match:
            return {
                'number': match.group(1),
                'title': match.group(2).strip() if match.group(2) else ''
            }
        return None

    def extract_rule_content(self, start_idx: int) -> tuple[List[str], int]:
        """Extract content for one rule until next rule or section"""
        lines = []
        idx = start_idx

        while idx < len(self.content):
            line = self.content[idx]

            # Stop at next rule
            if line.startswith('#### §'):
                break

            # Stop at next major section
            if line.startswith('#'):
                break

            lines.append(line)
            idx += 1

        return lines, idx

    def create_file(self, chapter: str, section: str, rule_num: str,
                   title: str, content: List[str], page: Optional[int] = None):
        """Create a single section file with front matter"""

        # Create directory structure
        if section:
            dir_path = self.output_dir / chapter / section
        else:
            dir_path = self.output_dir / chapter

        dir_path.mkdir(parents=True, exist_ok=True)

        # Create filename
        file_path = dir_path / f"s{rule_num.zfill(3)}.md"

        # Build front matter
        frontmatter = {
            'rule': f"§{rule_num}",
            'title': title if title else f"Section {rule_num}"
        }
        if page:
            frontmatter['page'] = page

        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            # Write front matter
            f.write('---\n')
            f.write(yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True))
            f.write('---\n\n')

            # Write content
            f.writelines(content)

        return file_path

    def extract_all(self):
        """Main extraction logic"""
        print(f"\n🔍 Extracting sections...")
        print(f"   Output: {self.output_dir}/\n")

        self.output_dir.mkdir(exist_ok=True)

        idx = 0
        files_created = 0
        current_chapter_name = None
        current_section_name = None

        while idx < len(self.content):
            line = self.content[idx]

            # Detect chapter
            chapter = self.detect_chapter(line)
            if chapter:
                # Get chapter name from next line
                if idx + 1 < len(self.content):
                    next_line = self.content[idx + 1]
                    if next_line.startswith('##'):
                        current_chapter_name = next_line.strip('#').strip().lower()
                        current_chapter_name = re.sub(r'[^a-z0-9]+', '_', current_chapter_name)
                        self.current_chapter = f"{chapter}_{current_chapter_name}"
                    else:
                        self.current_chapter = f"{chapter}_chapter"
                print(f"\n📂 Chapter: {self.current_chapter}")
                idx += 1
                continue

            # Detect section
            section = self.detect_section(line)
            if section:
                self.current_section = section
                print(f"   📁 Section: {section}")
                idx += 1
                continue

            # Detect rule
            rule_info = self.detect_rule(line)
            if rule_info and self.current_chapter:
                rule_num = rule_info['number']
                title = rule_info['title']

                # Extract content until next rule
                content, next_idx = self.extract_rule_content(idx + 1)

                # Create file
                file_path = self.create_file(
                    self.current_chapter,
                    self.current_section,
                    rule_num,
                    title,
                    content
                )

                files_created += 1
                print(f"      ✅ §{rule_num}: {title[:50]}... → {file_path.name}")

                idx = next_idx
                continue

            idx += 1

        print(f"\n✅ Extraction complete!")
        print(f"   Files created: {files_created}")
        print(f"   Output directory: {self.output_dir}/")

        # Summary
        self.print_summary()

    def print_summary(self):
        """Print directory structure summary"""
        print(f"\n📊 Directory Structure:")

        for chapter_dir in sorted(self.output_dir.iterdir()):
            if not chapter_dir.is_dir():
                continue

            file_count = 0
            for item in chapter_dir.rglob("*.md"):
                file_count += 1

            print(f"   {chapter_dir.name}/ ({file_count} files)")

            # Show sections
            for section_dir in sorted(chapter_dir.iterdir()):
                if section_dir.is_dir():
                    section_files = list(section_dir.glob("*.md"))
                    print(f"      {section_dir.name}/ ({len(section_files)} files)")

def main():
    # Paths
    project_root = Path(__file__).parent.parent.parent
    v7_file = project_root / "output" / "kales_sanskrit_grammar_v7.md"
    output_dir = project_root / "v8_sections"

    if not v7_file.exists():
        print(f"❌ Error: v7 file not found at {v7_file}")
        return

    # Extract
    extractor = SectionExtractor(v7_file, output_dir)
    extractor.load_v7()
    extractor.extract_all()

if __name__ == "__main__":
    main()
