#!/usr/bin/env python3
"""
Fix formatting issues in rule files according to MARKDOWN_SPEC.md
"""

from pathlib import Path
import re

def fix_rule_file(file_path):
    """Fix formatting issues in a single rule file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    changes = []

    # Fix 1: Remove rule number headers (## § N.)
    # The rule number is already in YAML, don't duplicate in content
    pattern = r'^## § \d+\.\s+(.+)$'
    if re.search(pattern, content, re.MULTILINE):
        # Replace with just the title
        content = re.sub(pattern, r'\1', content, flags=re.MULTILINE)
        changes.append("Removed duplicate rule number header")

    # Fix 2: Replace : with ḥ for visarga in IAST @[...] tags
    # Match @[...] tags and replace : with ḥ inside them
    def fix_visarga(match):
        iast_content = match.group(1)
        # Replace : with ḥ but be careful about actual colons in explanations
        # Only replace : that follows a consonant or vowel (Sanskrit word ending)
        fixed = re.sub(r'([a-zāīūṛḷṃśṣñṇṅṭḍ]):(?=\s|$|])', r'\1ḥ', iast_content)
        return f'@[{fixed}]'

    new_content = re.sub(r'@\[([^\]]+)\]', fix_visarga, content)
    if new_content != content:
        content = new_content
        changes.append("Fixed visarga : → ḥ in IAST")

    # Fix 3: Check for Devanagari in IAST tags (report only, manual fix needed)
    deva_in_iast = re.findall(r'@\[([^\]]*[\u0900-\u097F][^\]]*)\]', content)
    if deva_in_iast:
        changes.append(f"WARNING: Devanagari found in IAST tags: {deva_in_iast[:2]}")

    # Fix 4: Check for Latin in Devanagari tags (report only)
    latin_in_deva = re.findall(r'@deva\[([^\]]*[a-zA-Z][^\]]*)\]', content)
    if latin_in_deva:
        changes.append(f"WARNING: Latin found in @deva tags: {latin_in_deva[:2]}")

    # Only write if changes were made
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return changes

    return changes

# Process rules 1-41
print("Fixing formatting issues in rules 1-41...\n")

fixed_count = 0
for i in range(1, 42):
    rule_file = Path(f'phase3_rules/rule_{i:03d}.md')
    if not rule_file.exists():
        continue

    changes = fix_rule_file(rule_file)
    if changes:
        print(f"Rule {i:03d}:")
        for change in changes:
            print(f"  ✓ {change}")
        fixed_count += 1

print(f"\n{'='*60}")
print(f"Fixed {fixed_count} rule files")
print(f"{'='*60}")
