#!/usr/bin/env python3
"""
Phase 2 Validation Script
Ensures proper mapping from source pages to output files with correct internal page numbers
"""

import json
import re
import glob
from pathlib import Path
from collections import defaultdict

class Phase2Validator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        
    def log_error(self, msg):
        self.errors.append(f"❌ ERROR: {msg}")
        
    def log_warning(self, msg):
        self.warnings.append(f"⚠️  WARNING: {msg}")
        
    def log_info(self, msg):
        self.info.append(f"ℹ️  INFO: {msg}")
    
    def validate_source_coverage(self):
        """Check 1: Ensure all source page variants are discovered"""
        print("\n=== CHECK 1: Source Coverage ===")
        
        # Find all claude source files
        claude_files = sorted(glob.glob('phase1_ocr/claude/page_*.txt'))
        
        # Group by base page number
        page_groups = defaultdict(list)
        for f in claude_files:
            match = re.search(r'page_(\d+)([ab]?)\.txt', f)
            if match:
                base = match.group(1)
                variant = match.group(2) or 'base'
                page_groups[base].append((variant, f))
        
        total_files = 0
        for base, variants in sorted(page_groups.items())[:20]:  # Show first 20
            variant_str = ', '.join(v[0] for v in sorted(variants))
            if len(variants) > 1:
                self.log_info(f"Page {base} has variants: {variant_str}")
            total_files += len(variants)
        
        self.log_info(f"Total source files found: {total_files}")
        return page_groups
    
    def extract_internal_page(self, filepath):
        """Extract internal page number from file header"""
        try:
            with open(filepath, 'r', errors='ignore') as f:
                content = f.read(500)  # First 500 chars
                
                # Pattern 1: "N    SANSKRIT GRAMMAR"
                match = re.search(r'^(\d+)\s+SANSKRIT GRAMMAR', content, re.MULTILINE)
                if match:
                    return int(match.group(1))
                
                # Pattern 2: "§ N-M ]   CHAPTER   . N"
                match = re.search(r'§.*?[\.\s]+(\d+)\s*$', content.split('\n')[0])
                if match:
                    return int(match.group(1))
                
                # Pattern 3: Look for roman numerals in preface/contents
                if 'PREFACE' in content[:100]:
                    return 'preface'
                elif 'CONTENTS' in content[:100]:
                    return 'contents'
                elif 'ABBREVIATIONS' in content[:100]:
                    return 'abbreviations'
                    
                return None
        except Exception as e:
            self.log_error(f"Failed to read {filepath}: {e}")
            return None
    
    def extract_rules(self, filepath):
        """Extract rule numbers (§ N) from file"""
        try:
            with open(filepath, 'r', errors='ignore') as f:
                content = f.read()
                # Pattern: § N. or 3 N. (OCR error)
                rules = []
                for match in re.finditer(r'§\s*(\d+)\.', content):
                    rules.append(int(match.group(1)))
                # OCR corruption pattern
                for line in content.split('\n'):
                    match = re.match(r'^3\s+(\d+)\.\s+', line)
                    if match:
                        rules.append(int(match.group(1)))
                return sorted(set(rules))
        except:
            return []
    
    def validate_internal_page_sequence(self, page_groups):
        """Check 2: Ensure internal pages are sequential without gaps"""
        print("\n=== CHECK 2: Internal Page Sequence ===")
        
        # Build mapping: source file -> internal page
        internal_pages = []
        for base, variants in sorted(page_groups.items(), key=lambda x: int(x[0])):
            for variant, filepath in sorted(variants):
                internal = self.extract_internal_page(filepath)
                rules = self.extract_rules(filepath)
                
                if internal and isinstance(internal, int):
                    internal_pages.append({
                        'source': Path(filepath).name,
                        'internal': internal,
                        'rules': rules
                    })
        
        # Sort by internal page number
        internal_pages.sort(key=lambda x: x['internal'])
        
        # Check for gaps
        prev = None
        for entry in internal_pages[:30]:  # Show first 30
            internal = entry['internal']
            if prev is not None and internal > prev + 1:
                for missing in range(prev + 1, internal):
                    self.log_error(f"INTERNAL PAGE GAP: Page {missing} is missing!")
            
            rules_str = f"§{', §'.join(map(str, entry['rules'][:3]))}" if entry['rules'] else "no rules"
            print(f"  {entry['source']:20s} -> Internal p.{internal:3d} - {rules_str}")
            prev = internal
        
        return internal_pages
    
    def validate_rule_sequence(self, internal_pages):
        """Check 3: Ensure rule numbers are mostly sequential"""
        print("\n=== CHECK 3: Rule Number Sequence ===")
        
        all_rules = []
        for entry in internal_pages:
            for rule in entry['rules']:
                all_rules.append((rule, entry['internal'], entry['source']))
        
        all_rules.sort(key=lambda x: x[0])
        
        prev_rule = None
        for rule_num, internal, source in all_rules[:50]:  # Check first 50 rules
            if prev_rule and rule_num > prev_rule + 10:
                self.log_warning(f"Large gap in rules: §{prev_rule} -> §{rule_num} (page {internal})")
            prev_rule = rule_num
        
        self.log_info(f"Total rules found: {len(set(r[0] for r in all_rules))}")
        first_rule = all_rules[0][0] if all_rules else None
        last_rule = all_rules[-1][0] if all_rules else None
        self.log_info(f"Rule range: §{first_rule} to §{last_rule}")
    
    def validate_output_filename_convention(self):
        """Check 4: Output filenames should match internal page numbers"""
        print("\n=== CHECK 4: Output Filename Convention ===")
        
        cleaned_files = glob.glob('phase2_cleaned/page_*.md')
        
        for filepath in sorted(cleaned_files):
            # Read YAML frontmatter
            with open(filepath) as f:
                content = f.read()
                match = re.search(r'page_number:\s*(\d+)', content)
                internal_match = re.search(r'internal_page:\s*(\d+|[ivxIVX]+)', content)
                
                if match and internal_match:
                    filename_num = Path(filepath).stem.split('_')[1]
                    page_num = match.group(1)
                    internal_page = internal_match.group(1)

                    # The output filename should match the sequential page number,
                    # NOT the internal page
                    # Compare as integers to handle leading zeros
                    if int(filename_num) != int(page_num):
                        self.log_error(f"{filepath}: filename page_{filename_num} != page_number:{page_num}")
                    
                    print(f"  {Path(filepath).name:20s} -> page_number:{page_num:3s}, internal_page:{internal_page:8s}")
        
        self.log_info(f"Total cleaned files: {len(cleaned_files)}")
    
    def create_correct_mapping(self, page_groups):
        """Check 5: Create corrected source->output mapping"""
        print("\n=== CHECK 5: Corrected Mapping ===")

        # First, collect all source files with their metadata
        all_sources = []

        for base, variants in page_groups.items():
            for variant, filepath in variants:
                internal = self.extract_internal_page(filepath)
                rules = self.extract_rules(filepath)
                
                # Determine content type
                with open(filepath, 'r', errors='ignore') as f:
                    first_100 = f.read(100)
                    if 'PREFACE' in first_100:
                        content_type = 'preface'
                    elif 'CONTENTS' in first_100:
                        content_type = 'contents'
                    elif 'ABBREVIATIONS' in first_100:
                        content_type = 'abbreviations'
                    elif rules:
                        content_type = f"§{min(rules)}"
                    else:
                        content_type = 'unknown'

                # Determine image path for this source
                source_name = Path(filepath).name
                if 'claude' in filepath:
                    # claude images are alongside source files
                    image_path = str(Path(filepath).with_suffix('.png'))
                else:
                    # official_1931 images are in separate directory
                    # e.g., sources/official_1931/004.txt -> images/official_1931/004.png
                    filename = Path(filepath).stem  # e.g., "004" or "front_017"
                    image_path = f'phase1_ocr/images/official_1931/{filename}.png'

                # Check if image exists
                image_exists = Path(image_path).exists()

                all_sources.append({
                    'filepath': filepath,
                    'base': int(base),
                    'variant': variant,
                    'internal_page': internal,
                    'rules': rules,
                    'content_type': content_type,
                    'image_path': image_path,
                    'image_exists': image_exists
                })

        # Sort by base page number, then by internal page number (for variants)
        # This ensures page_013.txt (internal 5) comes before page_013a.txt (internal 6)
        def sort_key(entry):
            base = entry['base']
            internal = entry['internal_page']

            # Convert internal page to sortable value
            if isinstance(internal, int):
                return (base, internal)
            elif internal == 'preface':
                return (base, -4)
            elif internal == 'contents':
                return (base, -3)
            elif internal == 'abbreviations':
                return (base, -2)
            else:
                # Unknown - sort by variant letter
                variant_order = {'base': 0, 'a': 1, 'b': 2, 'c': 3}
                return (base, -1, variant_order.get(entry['variant'], 99))

        all_sources.sort(key=sort_key)

        # Create mapping with sequential output page numbers
        mapping = []
        output_page = 1

        for entry in all_sources:
            internal = entry['internal_page']
            rules = entry['rules']
            image_path = entry['image_path']
            image_exists = entry['image_exists']

            # Determine which source type (for dual-source tracking)
            if 'claude' in entry['filepath']:
                source_type = 'claude'
            elif 'official_1931' in entry['filepath']:
                source_type = 'official_1931'
            else:
                source_type = 'unknown'

            mapped_entry = {
                'output_page': output_page,
                'output_file': f'page_{output_page:03d}.md',
                'source_file': Path(entry['filepath']).name,
                'source_path': entry['filepath'],
                'source_type': source_type,
                'source_image': image_path,
                'image_exists': image_exists,
                'internal_page': internal,
                'rules': rules,
                'content_type': entry['content_type']
            }
            mapping.append(mapped_entry)

            # Warn about missing images
            if not image_exists:
                self.log_warning(f"Image missing for {mapped_entry['output_file']}: {image_path}")

            if output_page <= 20:
                internal_str = str(internal) if internal else '?'
                rules_str = f"§{', §'.join(map(str, rules[:2]))}" if rules else entry['content_type']
                img_status = "✓" if image_exists else "✗"
                print(f"{img_status} {mapped_entry['output_file']:15s} <- {mapped_entry['source_file']:20s} (internal p.{internal_str:>3s}) - {rules_str}")

            output_page += 1
        
        # Save corrected mapping
        with open('phase2_corrected_mapping.json', 'w') as f:
            json.dump(mapping, f, indent=2)
        
        self.log_info(f"Saved corrected mapping to phase2_corrected_mapping.json")
        return mapping
    
    def run_all_checks(self):
        """Run all validation checks"""
        print("=" * 80)
        print("PHASE 2 VALIDATION CHECKS")
        print("=" * 80)
        
        page_groups = self.validate_source_coverage()
        internal_pages = self.validate_internal_page_sequence(page_groups)
        self.validate_rule_sequence(internal_pages)
        self.validate_output_filename_convention()
        corrected_mapping = self.create_correct_mapping(page_groups)
        
        # Print summary
        print("\n" + "=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)
        
        for msg in self.errors:
            print(msg)
        for msg in self.warnings:
            print(msg)
        for msg in self.info:
            print(msg)
        
        if self.errors:
            print(f"\n❌ VALIDATION FAILED: {len(self.errors)} errors found")
            return False
        else:
            print(f"\n✅ VALIDATION PASSED")
            if self.warnings:
                print(f"   ({len(self.warnings)} warnings)")
            return True

if __name__ == '__main__':
    validator = Phase2Validator()
    success = validator.run_all_checks()
    exit(0 if success else 1)
