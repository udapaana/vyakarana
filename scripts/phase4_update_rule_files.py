#!/usr/bin/env python3
"""
Phase 4: Update all rule files to use unified images

This script:
1. Removes [Internal page: NNN] markers from content
2. Updates image paths to point to phase4_images/NNN.png
3. Uses internal page numbers from YAML frontmatter
"""

import re
from pathlib import Path

RULES_DIR = Path("phase4_rules")
MAPPING_FILE = Path("phase4_images/PAGE_MAPPING.txt")

def load_page_mapping():
    """Load external -> internal page mapping"""
    mapping = {}
    
    if not MAPPING_FILE.exists():
        print(f"ERROR: {MAPPING_FILE} not found. Run phase4_create_unified_images.py first.")
        return None
    
    with MAPPING_FILE.open() as f:
        for line in f:
            if '|' in line and not line.startswith(('PHASE', '=', '-', 'Internal')):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 2 and parts[0].isdigit():
                    internal = int(parts[0])
                    external = int(parts[1])
                    mapping[external] = internal
    
    return mapping

def extract_page_from_yaml(content: str) -> int:
    """Extract page number from YAML frontmatter"""
    match = re.search(r'^page:\s*(\d+)', content, re.MULTILINE)
    if match:
        return int(match.group(1))
    return None

def update_rule_file(rule_file: Path, page_mapping: dict) -> bool:
    """Update a single rule file"""
    try:
        content = rule_file.read_text(encoding='utf-8')
        original_content = content
        
        # Extract page from YAML
        page_num = extract_page_from_yaml(content)
        if not page_num:
            return False
        
        # Get internal page number
        internal_page = page_mapping.get(page_num, page_num)
        
        # Remove [Internal page: NNN] markers
        content = re.sub(r'\[Internal page:\s*\d+\]\s*\n?', '', content)
        
        # Update image path in YAML frontmatter
        # Change: image: /images/page_NNN.jpg
        # To:     image: /images/NNN.png
        content = re.sub(
            r'image:\s*/images/page_\d+\.jpg',
            f'image: /images/{internal_page:03d}.png',
            content
        )
        
        # Also handle format: image: /images/NNN.jpg
        content = re.sub(
            r'image:\s*/images/\d+\.jpg',
            f'image: /images/{internal_page:03d}.png',
            content
        )
        
        # Write back if changed
        if content != original_content:
            rule_file.write_text(content, encoding='utf-8')
            return True
        
        return False
        
    except Exception as e:
        print(f"  ERROR processing {rule_file.name}: {e}")
        return False

def update_all_rules():
    """Update all rule files to use Phase 4 images"""
    
    print("=" * 70)
    print("PHASE 4: UPDATE RULE FILES")
    print("=" * 70)
    
    # Load mapping
    print("\n1. Loading page mapping...")
    page_mapping = load_page_mapping()
    if not page_mapping:
        return
    print(f"   Loaded {len(page_mapping)} page mappings")
    
    # Update rules
    print("\n2. Updating rule files...")
    
    updated_count = 0
    skipped_count = 0
    
    for rule_file in sorted(RULES_DIR.glob("rule_*.md")):
        if update_rule_file(rule_file, page_mapping):
            updated_count += 1
            if updated_count % 100 == 0:
                print(f"   Updated {updated_count} files...")
        else:
            skipped_count += 1
    
    print("\n" + "=" * 70)
    print("UPDATE COMPLETE")
    print("=" * 70)
    print(f"  Updated: {updated_count} files")
    print(f"  Skipped: {skipped_count} files (no changes needed)")
    print(f"  TOTAL:   {updated_count + skipped_count} files")
    print("=" * 70)
    
    # Verify a sample
    print("\n3. Verification sample:")
    sample_files = sorted(RULES_DIR.glob("rule_*.md"))[:3]
    for rule_file in sample_files:
        content = rule_file.read_text()
        match = re.search(r'image:\s*(.+)', content)
        if match:
            print(f"   {rule_file.name}: {match.group(1)}")

if __name__ == "__main__":
    update_all_rules()
