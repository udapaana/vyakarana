#!/usr/bin/env python3
"""Convert ALL old YAML schema rules to new format"""
import re
from pathlib import Path

RULES_DIR = Path("phase4_rules")

def convert_schema(file: Path) -> bool:
    """Convert a rule from old schema to new"""
    content = file.read_text()
    
    # Skip if already new schema
    if 'rule:' in content and 'rule_number:' not in content:
        return False
    
    original = content
    
    # Convert old fields to new
    content = re.sub(r'rule_number:\s*(\d+)', r'rule: § \1', content)
    content = re.sub(r'rule_id:\s*"§\s*(\d+)"\s*\n', '', content)  # Remove duplicate
    content = re.sub(r'page_start:\s*(\d+)', r'page: \1', content)
    content = re.sub(r'page_end:\s*\d+\s*\n', '', content)
    content = re.sub(r'examples_count:\s*\d+\s*\n', '', content)
    content = re.sub(r'has_table:\s*(true|false)\s*\n', '', content)
    content = re.sub(r'has_footnotes:\s*(true|false)\s*\n', '', content)
    
    # Fix source_pages format
    content = re.sub(
        r'source_pages:\s*\n\s*-\s*"?page_(\d+)\.txt"?',
        lambda m: f'source_pages:\n  dli: [{int(m.group(1))}]\n  official_1931: [{int(m.group(1)):03d}]',
        content
    )
    
    # Add missing standard fields if not present
    if 'subsections:' not in content:
        content = re.sub(r'(topics:)', r'subsections: []\n\n\1', content)
    
    if 'hierarchy:' not in content:
        chapter_match = re.search(r'chapter:\s*"?([^"\n]+)"?', content)
        section_match = re.search(r'section:\s*"?([^"\n]+)"?', content)
        
        if chapter_match and section_match:
            chapter = chapter_match.group(1).strip()
            section = section_match.group(1).strip()
            
            hierarchy = f"\nhierarchy:\n  chapter: {chapter}\n  section: {section}\n"
            content = re.sub(r'(cross_refs:)', hierarchy + r'\1', content)
    
    if 'confidence:' not in content:
        content = re.sub(r'(image:)', r'confidence: medium\n\n\1', content)
    
    if 'footnotes:' not in content:
        content = re.sub(r'(confidence:)', r'footnotes: []\n\n\1', content)
    
    # Clean up extra newlines
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    if content != original:
        file.write_text(content, encoding='utf-8')
        return True
    
    return False

print("=" * 70)
print("CONVERTING ALL OLD SCHEMA RULES")
print("=" * 70)

converted = 0
skipped = 0

for file in sorted(RULES_DIR.glob("rule_*.md")):
    content = file.read_text()
    if 'rule_number:' in content:
        if convert_schema(file):
            converted += 1
            if converted % 50 == 0:
                print(f"  Converted {converted} rules...")
        else:
            skipped += 1

print("\n" + "=" * 70)
print(f"Converted: {converted} rules")
print(f"Skipped:   {skipped} rules")
print("=" * 70)
