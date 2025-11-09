#!/usr/bin/env python3
"""
Fix Sanskrit tagging in alphabet rules (§1-38)
- Separate Devanagari and IAST properly
- Keep English words (or, and, but, etc.) outside tags
"""
import re
from pathlib import Path
from indic_transliteration import sanscript

RULES_DIR = Path("phase4_rules")

def clean_tag_content(text):
    """Remove English words from inside tags"""
    # Common English words that shouldn't be in tags
    english_words = ['or', 'and', 'but', 'as', 'the', 'a', 'an', 'is', 'are', 'when', 'if', 'not']
    
    # Split on English words and re-tag each part
    pattern = r'\b(' + '|'.join(english_words) + r')\b'
    
    parts = re.split(pattern, text, flags=re.IGNORECASE)
    result = []
    
    for i, part in enumerate(parts):
        part = part.strip()
        if not part:
            continue
        if part.lower() in english_words:
            result.append(f' {part} ')
        else:
            result.append(part)
    
    return ''.join(result)

def fix_alphabet_rule(rule_num):
    """Fix tagging for a single alphabet rule"""
    file = RULES_DIR / f"rule_{rule_num:03d}.md"
    if not file.exists():
        return False
    
    content = file.read_text()
    
    # For alphabet rules, we need both Devanagari and IAST
    # Find all @[] tags that might contain mixed content
    
    def fix_tag(match):
        tag_content = match.group(1)
        
        # Check if it contains English words
        if any(word in tag_content.lower() for word in ['or', 'and', 'but']):
            # Split and re-tag
            cleaned = clean_tag_content(tag_content)
            # Re-wrap non-English parts
            parts = re.split(r'\s+(or|and|but)\s+', cleaned, flags=re.IGNORECASE)
            tagged_parts = []
            for part in parts:
                if part.strip().lower() in ['or', 'and', 'but']:
                    tagged_parts.append(f' {part} ')
                elif part.strip():
                    tagged_parts.append(f'@[{part.strip()}]')
            return ''.join(tagged_parts)
        
        return match.group(0)
    
    # Fix @[...] tags
    content = re.sub(r'@\[([^\]]+)\]', fix_tag, content)
    
    file.write_text(content, encoding='utf-8')
    return True

print("=" * 70)
print("FIXING ALPHABET RULE TAGGING (§1-38)")
print("=" * 70)

fixed = 0
for num in range(1, 39):
    if fix_alphabet_rule(num):
        fixed += 1

print(f"\nFixed {fixed} alphabet rules")
print("=" * 70)
