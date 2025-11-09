#!/usr/bin/env python3
"""Convert old YAML schema rules to new format"""
import re
from pathlib import Path

RULES_DIR = Path("phase3_rules")

old_schema_rules = [66, 507, 527, 529, 530, 531, 534, 537, 538, 539, 540, 542, 543, 545, 548, 549, 550, 560, 562, 583, 592, 594, 597, 598, 599, 600, 639, 911, 912, 913, 914, 915, 916, 917, 918, 919, 920]

def convert_schema(rule_num: int) -> bool:
    """Convert a rule from old schema to new"""
    file = RULES_DIR / f"rule_{rule_num:03d}.md"
    if not file.exists():
        return False
    
    content = file.read_text()
    
    # Skip if already new schema
    if 'rule:' in content and 'rule_number:' not in content:
        return False
    
    # Convert old fields to new
    content = re.sub(r'rule_number:\s*(\d+)', r'rule: § \1', content)
    content = re.sub(r'rule_id:\s*"§\s*(\d+)"', r'', content)  # Remove duplicate
    content = re.sub(r'page_start:\s*(.+)', r'page: \1', content)
    content = re.sub(r'page_end:.+\n', '', content)
    content = re.sub(r'examples_count:.+\n', '', content)
    content = re.sub(r'has_table:.+\n', '', content)
    content = re.sub(r'has_footnotes:.+\n', '', content)
    
    # Fix source_pages format
    content = re.sub(
        r'source_pages:\s*\n\s*-\s*"page_(\d+)\.txt"',
        lambda m: f'source_pages:\n  dli: [{int(m.group(1))}]\n  official_1931: [{int(m.group(1)):03d}]',
        content
    )
    
    # Add missing fields
    if 'subsections:' not in content:
        content = re.sub(
            r'(topics:)',
            r'subsections: []\n\1',
            content
        )
    
    if 'hierarchy:' not in content:
        # Extract chapter and section
        chapter_match = re.search(r'chapter:\s*"?([^"\n]+)"?', content)
        section_match = re.search(r'section:\s*"?([^"\n]+)"?', content)
        
        if chapter_match and section_match:
            chapter = chapter_match.group(1).strip()
            section = section_match.group(1).strip()
            
            hierarchy = f"\nhierarchy:\n  chapter: {chapter}\n  section: {section}\n"
            content = re.sub(
                r'(cross_refs:)',
                hierarchy + r'\1',
                content
            )
    
    if 'confidence:' not in content:
        content = re.sub(
            r'(image:)',
            r'confidence: medium\n\n\1',
            content
        )
    
    if 'footnotes:' not in content:
        content = re.sub(
            r'(confidence:)',
            r'footnotes: []\n\n\1',
            content
        )
    
    # Clean up any double newlines in YAML
    content = re.sub(r'\n\n+---', '\n---', content)
    content = re.sub(r'---\n\n+', '---\n', content)
    
    file.write_text(content, encoding='utf-8')
    return True

print("=" * 70)
print("CONVERTING OLD SCHEMA RULES")
print("=" * 70)

converted = 0
skipped = 0

for rule_num in old_schema_rules:
    if convert_schema(rule_num):
        converted += 1
        if converted % 10 == 0:
            print(f"  Converted {converted} rules...")
    else:
        skipped += 1

print("\n" + "=" * 70)
print(f"Converted: {converted} rules")
print(f"Skipped:   {skipped} rules (already new format)")
print("=" * 70)
