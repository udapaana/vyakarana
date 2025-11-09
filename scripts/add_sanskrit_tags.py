#!/usr/bin/env python3
"""
Add Sanskrit tagging to extracted rules.
- Alphabet chapters (§1-38): Use both @deva[] and @[IAST]
- Other chapters (§39-972): Use only @deva[]
"""
import re
from pathlib import Path
from indic_transliteration import sanscript

RULES_DIR = Path("phase3_rules")

def tag_devanagari_text(text: str, include_iast: bool = False) -> str:
    """
    Tag Devanagari text in content.
    If include_iast=True, add IAST transliteration (for alphabet chapters).
    Otherwise, just wrap in @deva[] tags.
    """
    # Pattern to find Devanagari text (continuous Devanagari characters)
    # Include common Devanagari punctuation like danda (।), double danda (॥)
    deva_pattern = r'([ऀ-ॿ]+(?:\s+[ऀ-ॿ]+)*)'
    
    def replace_deva(match):
        deva_text = match.group(1).strip()
        
        # Skip if already tagged
        if '@deva[' in text[max(0, match.start()-10):match.start()]:
            return match.group(0)
        
        # Just Devanagari for most rules
        if not include_iast:
            return f'@deva[{deva_text}]'
        
        # Devanagari + IAST for alphabet chapters
        try:
            iast = sanscript.transliterate(deva_text, sanscript.DEVANAGARI, sanscript.IAST)
            return f'@deva[{deva_text}] @[{iast}]'
        except:
            # If transliteration fails, just use Devanagari
            return f'@deva[{deva_text}]'
    
    return re.sub(deva_pattern, replace_deva, text)

def process_rule_file(rule_num: int, dry_run: bool = False) -> bool:
    """Process a single rule file to add Sanskrit tags"""
    rule_file = RULES_DIR / f"rule_{rule_num:03d}.md"
    
    if not rule_file.exists():
        return False
    
    content = rule_file.read_text(encoding='utf-8')
    
    # Skip if already tagged or missing from OCR
    if '@deva[' in content or 'MISSING FROM OCR' in content:
        return False
    
    # Skip if it's a stub with no content
    if 'chapter: TBD' in content and len(content) < 500:
        return False
    
    # Determine if this is an alphabet chapter (§1-38)
    include_iast = (rule_num <= 38)
    
    # Split into YAML frontmatter and content
    parts = content.split('---\n', 2)
    if len(parts) < 3:
        return False
    
    yaml_front = parts[1]
    body = parts[2]
    
    # Tag the body content
    tagged_body = tag_devanagari_text(body, include_iast=include_iast)
    
    # Skip if no changes
    if tagged_body == body:
        return False
    
    # Remove the AUTO-EXTRACTED comment if present
    tagged_body = tagged_body.replace('<!-- AUTO-EXTRACTED: Needs Sanskrit tagging review -->\n', '')
    
    # Reconstruct file
    new_content = f"---\n{yaml_front}---\n{tagged_body}"
    
    if dry_run:
        print(f"§{rule_num}: Would tag (IAST={'yes' if include_iast else 'no'})")
        return True
    
    rule_file.write_text(new_content, encoding='utf-8')
    print(f"§{rule_num}: Tagged ({'with IAST' if include_iast else 'Deva only'})")
    return True

def main():
    import sys
    
    dry_run = '--dry-run' in sys.argv
    
    print("=" * 70)
    print("SANSKRIT TAGGING PROCESSOR")
    print("=" * 70)
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print()
    
    tagged_count = 0
    skipped_count = 0
    
    for rule_num in range(39, 973):
        if process_rule_file(rule_num, dry_run=dry_run):
            tagged_count += 1
        else:
            skipped_count += 1
    
    print()
    print("=" * 70)
    print(f"Tagged: {tagged_count} rules")
    print(f"Skipped: {skipped_count} rules (already tagged or no content)")
    print("=" * 70)

if __name__ == "__main__":
    main()
