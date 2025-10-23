#!/usr/bin/env python3
"""
Comprehensive verification of the v8 extraction

Checks:
1. Structure - Expected chapters/sections exist
2. Section naming - Folders match actual section names
3. Content - Files have proper content, no overlaps
4. Boundaries - No missing content between files
5. Consistency - Rule numbers sequential, no duplicates
6. Front matter - Valid YAML, correct rule numbers
"""

import json
import yaml
import re
from pathlib import Path
from collections import defaultdict

class ExtractionVerifier:
    def __init__(self, v7_path: Path, index_path: Path, sections_path: Path):
        self.v7_path = v7_path
        self.index_path = index_path
        self.sections_path = sections_path
        self.errors = []
        self.warnings = []

        # Load v7 content
        with open(v7_path, 'r', encoding='utf-8') as f:
            self.v7_lines = f.readlines()

        # Load index
        with open(index_path, 'r', encoding='utf-8') as f:
            self.index = json.load(f)

    def verify_all(self):
        """Run all verification checks"""
        print("🔍 COMPREHENSIVE VERIFICATION")
        print("=" * 80)

        self.verify_structure()
        self.verify_section_naming()
        self.verify_content()
        self.verify_boundaries()
        self.verify_consistency()
        self.verify_front_matter()

        self.print_summary()

    def verify_structure(self):
        """Check that all expected chapters/sections exist"""
        print("\n📊 1. STRUCTURE VERIFICATION")
        print("-" * 80)

        # Expected from Table of Contents
        expected_chapters = {
            'I': 'The Alphabet',
            'II': 'Rules of Sandhi',
            'III': 'Declension',
            'IV': 'Pronouns',
            'V': 'Numerals',
            'VI': 'Degrees of Comparison',  # Known missing
            'VII': 'Compounds',
            'VIII': 'Feminine Bases',
            'IX': 'Secondary Affixes',
            'X': 'Gender',
            'XI': 'Indeclinables',
            'XII': 'Conjugation of Verbs',
            'XIII': '???',
            'XIV': 'Verbal Derivatives',
            'XV': 'Syntax'
        }

        found_chapters = {ch['number'] for ch in self.index['chapters']}

        for num, name in expected_chapters.items():
            if num in found_chapters:
                print(f"  ✅ Chapter {num:>4}: {name}")
            else:
                self.errors.append(f"Missing Chapter {num}: {name}")
                print(f"  ❌ Chapter {num:>4}: {name} - MISSING")

        # Check for unexpected chapters
        for num in found_chapters:
            if num not in expected_chapters:
                self.warnings.append(f"Unexpected chapter {num} found")
                print(f"  ⚠️  Chapter {num:>4}: UNEXPECTED")

    def verify_section_naming(self):
        """Verify section folder names match actual section names"""
        print("\n📁 2. SECTION NAMING VERIFICATION")
        print("-" * 80)

        for chapter in self.index['chapters']:
            chapter_num = chapter['number']
            chapter_dirs = list(self.sections_path.glob(f"*_chapter_{chapter_num.lower()}"))

            if not chapter_dirs:
                continue

            chapter_dir = chapter_dirs[0]
            print(f"\n  Chapter {chapter_num}: {chapter_dir.name}/")

            for section_idx, section in enumerate(chapter.get('sections', []), 1):
                section_title = section['title']
                section_slug = self._slugify(section_title)
                expected_dir = f"{section_idx:02d}_{section_slug}"

                # Find actual directory
                section_dirs = list(chapter_dir.glob(f"{section_idx:02d}_*"))

                if not section_dirs:
                    self.errors.append(f"Chapter {chapter_num}, Section {section_idx}: Directory not found")
                    print(f"    ❌ {expected_dir}/ - NOT FOUND")
                    continue

                actual_dir = section_dirs[0]
                actual_name = actual_dir.name

                # Check if names match (allowing for slug differences)
                if actual_name != expected_dir:
                    # Check if it's just a minor slug difference
                    if actual_name.startswith(f"{section_idx:02d}_"):
                        self.warnings.append(f"Chapter {chapter_num}, Section {section_idx}: Name mismatch - expected '{expected_dir}', got '{actual_name}'")
                        print(f"    ⚠️  {actual_name}/ (expected: {expected_dir}/)")
                    else:
                        self.errors.append(f"Chapter {chapter_num}, Section {section_idx}: Wrong section number in '{actual_name}'")
                        print(f"    ❌ {actual_name}/ (expected: {expected_dir}/)")
                else:
                    print(f"    ✅ {actual_name}/ - \"{section_title[:50]}...\"")

    def verify_content(self):
        """Check that files have proper content"""
        print("\n📄 3. CONTENT VERIFICATION")
        print("-" * 80)

        empty_files = []
        malformed_files = []
        heading_only_files = []

        for md_file in self.sections_path.rglob("*.md"):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse YAML front matter and content
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    body = parts[2].strip()

                    # Check if it's just a heading with no content
                    if body and len(body) < 30 and body.endswith(':—'):
                        heading_only_files.append(str(md_file.relative_to(self.sections_path)))
                    elif len(body.strip()) < 10:
                        empty_files.append(str(md_file.relative_to(self.sections_path)))
                else:
                    empty_files.append(str(md_file.relative_to(self.sections_path)))
            else:
                # Check for empty content (legacy check for files without front matter)
                if len(content.strip()) < 50:
                    empty_files.append(str(md_file.relative_to(self.sections_path)))

            # Check for YAML front matter
            if not content.startswith('---'):
                malformed_files.append(str(md_file.relative_to(self.sections_path)))

            # Check for markdown headers that shouldn't be there
            lines = content.split('\n')
            in_front_matter = False
            content_started = False

            for line in lines:
                if line.strip() == '---':
                    if not content_started:
                        in_front_matter = not in_front_matter
                        if not in_front_matter:
                            content_started = True
                    continue

                if content_started and line.strip().startswith('#'):
                    self.warnings.append(f"{md_file.name}: Contains markdown header in content: {line[:60]}")

        if heading_only_files:
            print(f"\n  ℹ️  Heading-only rules ({len(heading_only_files)}) - These are section headers:")
            for f in heading_only_files[:5]:
                print(f"     - {f}")
            if len(heading_only_files) > 5:
                print(f"     ... and {len(heading_only_files) - 5} more")

        if empty_files:
            print(f"\n  ❌ Empty/tiny files ({len(empty_files)}):")
            for f in empty_files[:10]:
                print(f"     - {f}")
            if len(empty_files) > 10:
                print(f"     ... and {len(empty_files) - 10} more")
            self.errors.extend([f"Empty file: {f}" for f in empty_files])

        if malformed_files:
            print(f"\n  ❌ Malformed files (no front matter): {len(malformed_files)}")
            for f in malformed_files[:10]:
                print(f"     - {f}")
            self.errors.extend([f"Malformed: {f}" for f in malformed_files])

        if not empty_files and not malformed_files:
            print(f"  ✅ All files have content and proper front matter")

    def verify_boundaries(self):
        """Check for content overlaps and gaps"""
        print("\n🔗 4. BOUNDARY VERIFICATION")
        print("-" * 80)

        overlaps = []
        gaps = []

        for chapter in self.index['chapters']:
            for section in chapter.get('sections', []):
                rules = section.get('rules', [])

                for i, rule in enumerate(rules):
                    if i + 1 < len(rules):
                        next_rule = rules[i + 1]

                        # Check for gap (more than 10 lines between rules)
                        gap_size = next_rule['start_line'] - rule['start_line']

                        # Get actual file content to check what was extracted
                        rule_num = rule['number']
                        # Find the file
                        files = list(self.sections_path.rglob(f"s{int(rule_num):03d}.md"))

                        if files:
                            with open(files[0], 'r', encoding='utf-8') as f:
                                extracted = f.read()

                            # Check if extracted content contains content from next rule
                            next_rule_start = self.v7_lines[next_rule['start_line'] - 1][:50]
                            if next_rule_start.strip() in extracted:
                                overlaps.append(f"§{rule_num} contains content from §{next_rule['number']}")

        if overlaps:
            print(f"  ❌ Overlapping content ({len(overlaps)}):")
            for overlap in overlaps[:10]:
                print(f"     - {overlap}")
            self.errors.extend(overlaps)
        else:
            print(f"  ✅ No content overlaps detected")

    def verify_consistency(self):
        """Check rule number consistency"""
        print("\n🔢 5. CONSISTENCY VERIFICATION")
        print("-" * 80)

        all_rules = defaultdict(list)

        for chapter in self.index['chapters']:
            for section in chapter.get('sections', []):
                for rule in section.get('rules', []):
                    rule_num = rule['number']
                    all_rules[rule_num].append(f"Chapter {chapter['number']}")

        # Check for duplicates
        duplicates = {num: locations for num, locations in all_rules.items() if len(locations) > 1}

        if duplicates:
            print(f"  ⚠️  Duplicate rule numbers ({len(duplicates)}):")
            for num, locations in list(duplicates.items())[:10]:
                print(f"     - §{num}: appears in {', '.join(locations)}")
            self.warnings.extend([f"Duplicate §{num} in {locations}" for num, locations in duplicates.items()])
        else:
            print(f"  ✅ No duplicate rule numbers")

        # Check for missing sequences
        rule_nums = sorted([int(n) for n in all_rules.keys() if n.isdigit()])
        if rule_nums:
            expected_range = range(1, max(rule_nums) + 1)
            missing = [n for n in expected_range if n not in rule_nums]

            if missing and len(missing) < 50:  # Don't spam if many are missing
                print(f"  ⚠️  Missing rule numbers in sequence: {missing[:20]}")
                self.warnings.append(f"Missing {len(missing)} rule numbers in sequence")

    def verify_front_matter(self):
        """Verify YAML front matter in all files"""
        print("\n📋 6. FRONT MATTER VERIFICATION")
        print("-" * 80)

        invalid_yaml = []
        missing_rule = []
        wrong_rule_num = []

        for md_file in self.sections_path.rglob("*.md"):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract front matter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    try:
                        fm = yaml.safe_load(parts[1])

                        # Check for 'rule' field
                        if 'rule' not in fm:
                            missing_rule.append(str(md_file.relative_to(self.sections_path)))
                        else:
                            # Extract expected rule number from filename
                            match = re.search(r's(\d+)\.md$', md_file.name)
                            if match:
                                expected_num = int(match.group(1))
                                actual_rule = fm['rule']
                                # Extract number from §N format
                                actual_match = re.match(r'§(\d+)', str(actual_rule))
                                if actual_match:
                                    actual_num = int(actual_match.group(1))
                                    if actual_num != expected_num:
                                        wrong_rule_num.append(f"{md_file.name}: has §{actual_num}, expected §{expected_num}")

                    except yaml.YAMLError:
                        invalid_yaml.append(str(md_file.relative_to(self.sections_path)))

        if invalid_yaml:
            print(f"  ❌ Invalid YAML ({len(invalid_yaml)}):")
            for f in invalid_yaml[:10]:
                print(f"     - {f}")
            self.errors.extend([f"Invalid YAML: {f}" for f in invalid_yaml])

        if missing_rule:
            print(f"  ❌ Missing 'rule' field ({len(missing_rule)}):")
            for f in missing_rule[:10]:
                print(f"     - {f}")
            self.errors.extend([f"Missing rule field: {f}" for f in missing_rule])

        if wrong_rule_num:
            print(f"  ❌ Wrong rule numbers ({len(wrong_rule_num)}):")
            for err in wrong_rule_num[:10]:
                print(f"     - {err}")
            self.errors.extend(wrong_rule_num)

        if not invalid_yaml and not missing_rule and not wrong_rule_num:
            print(f"  ✅ All front matter valid and consistent")

    def print_summary(self):
        """Print verification summary"""
        print("\n" + "=" * 80)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 80)

        print(f"\n  Errors:   {len(self.errors)}")
        print(f"  Warnings: {len(self.warnings)}")

        if self.errors:
            print(f"\n  ❌ ERRORS ({len(self.errors)}):")
            for error in self.errors[:20]:
                print(f"     - {error}")
            if len(self.errors) > 20:
                print(f"     ... and {len(self.errors) - 20} more")

        if self.warnings:
            print(f"\n  ⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:20]:
                print(f"     - {warning}")
            if len(self.warnings) > 20:
                print(f"     ... and {len(self.warnings) - 20} more")

        if not self.errors and not self.warnings:
            print("\n  ✅ ALL CHECKS PASSED!")

        return len(self.errors) == 0

    def _slugify(self, text: str) -> str:
        """Convert text to filesystem-safe slug"""
        # Remove Sanskrit tags
        text = re.sub(r'@\[([^\]]+)\]', r'\1', text)
        slug = text.lower()
        slug = re.sub(r'[^a-z0-9]+', '_', slug)
        slug = slug.strip('_')
        if len(slug) > 50:
            slug = slug[:50].rstrip('_')
        return slug

def main():
    project_root = Path(__file__).parent.parent.parent
    v7_file = project_root / "output" / "kales_sanskrit_grammar_v7.md"
    index_file = project_root / "sections_index.json"
    sections_dir = project_root / "v8_sections"

    verifier = ExtractionVerifier(v7_file, index_file, sections_dir)
    success = verifier.verify_all()

    exit(0 if success else 1)

if __name__ == "__main__":
    main()
