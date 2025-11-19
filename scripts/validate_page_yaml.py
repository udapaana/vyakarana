#!/usr/bin/env python3
"""
Validate Phase 2 cleaned pages for YAML accuracy
Catches common errors:
1. page_number doesn't match filename
2. rules_starting doesn't match actual § N. patterns in content
3. Duplicate content across multiple files
"""

import re
import sys
import glob
from pathlib import Path
from collections import defaultdict

class PageYAMLValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate_all_pages(self):
        """Validate all cleaned pages"""
        print("=" * 80)
        print("PHASE 2 PAGE YAML VALIDATION")
        print("=" * 80)

        pages = sorted(glob.glob('phase2_cleaned/page_*.md'))

        if not pages:
            print("\n❌ No cleaned pages found in phase2_cleaned/")
            return False

        print(f"\nValidating {len(pages)} pages...\n")

        content_hashes = defaultdict(list)

        for page_path in pages:
            filename = Path(page_path).name
            page_num_from_filename = int(filename.split('_')[1].split('.')[0])

            with open(page_path) as f:
                content = f.read()

            # Extract YAML
            try:
                page_number = int(re.search(r'page_number:\s*(\d+)', content).group(1))
                rules_starting_str = re.search(r'rules_starting:\s*(\[.*?\])', content).group(1)
                rules_starting = eval(rules_starting_str)
            except Exception as e:
                self.errors.append(f"{filename}: Failed to parse YAML - {e}")
                continue

            # Check 1: page_number matches filename
            if page_number != page_num_from_filename:
                self.errors.append(
                    f"{filename}: page_number={page_number} doesn't match "
                    f"filename (expected {page_num_from_filename})"
                )

            # Check 2: rules_starting matches actual content
            yaml_end = content.find('---', 10)
            if yaml_end == -1:
                self.errors.append(f"{filename}: Could not find second --- marker")
                continue

            actual_content = content[yaml_end+3:]
            # Match both § N. and § N  (with period or space)
            actual_rules = [f"§ {n}" for n in re.findall(r'^§\s*(\d+)[.\s]', actual_content, re.MULTILINE)]

            if rules_starting != actual_rules:
                self.errors.append(
                    f"{filename}: rules_starting={rules_starting} but "
                    f"actual content has {actual_rules}"
                )

            # Check 3: Track content for duplicates
            # Use first 200 chars of content as hash
            content_hash = actual_content[:200].strip()
            content_hashes[content_hash].append(filename)

        # Report duplicates
        for content_hash, filenames in content_hashes.items():
            if len(filenames) > 1:
                self.errors.append(
                    f"DUPLICATE CONTENT: {', '.join(filenames)} have identical content"
                )

        # Print summary
        print("\n" + "=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)

        if self.errors:
            print("\n❌ ERRORS FOUND:\n")
            for error in self.errors:
                print(f"  ❌ {error}")

        if self.warnings:
            print("\n⚠️  WARNINGS:\n")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ ALL VALIDATIONS PASSED")
            print(f"   {len(pages)} pages validated successfully")
            return True
        else:
            print(f"\n❌ VALIDATION FAILED: {len(self.errors)} errors, {len(self.warnings)} warnings")
            return False

if __name__ == '__main__':
    validator = PageYAMLValidator()
    success = validator.validate_all_pages()
    sys.exit(0 if success else 1)
