#!/usr/bin/env python3
"""Deep search for the 11 missing rules across all OCR pages"""
import re
from pathlib import Path

OCR_DIR = Path("phase1_ocr/sources/official_1931")
missing = [37, 72, 255, 271, 361, 363, 381, 519, 682, 830, 839, 879]

print("=" * 70)
print("DEEP SEARCH FOR 11 MISSING RULES")
print("=" * 70)

found_rules = {}

for rule_num in missing:
    print(f"\n§{rule_num}:", end=" ")
    
    # Search all pages
    for page_file in sorted(OCR_DIR.glob("*.txt")):
        content = page_file.read_text(encoding='utf-8', errors='ignore')
        
        # Multiple search patterns
        patterns = [
            rf'§\s*{rule_num}(?:\.|[^\d])',  # § N.
            rf'§\s*{rule_num}\s+[A-Z]',        # § N TITLE
            rf'\b{rule_num}\.\s+[A-Z]',        # N. TITLE
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                # Get context
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 100)
                context = content[start:end].replace('\n', ' ')
                
                found_rules[rule_num] = {
                    'page': int(page_file.stem),
                    'context': context[:150]
                }
                print(f"✓ FOUND on page {page_file.stem}")
                print(f"     Context: {context[:100]}...")
                break
        
        if rule_num in found_rules:
            break
    
    if rule_num not in found_rules:
        print("✗ NOT FOUND")

print("\n" + "=" * 70)
print(f"RESULTS: Found {len(found_rules)}/11 missing rules")
print("=" * 70)

if found_rules:
    print("\nFOUND RULES:")
    for rule_num, info in sorted(found_rules.items()):
        print(f"  §{rule_num}: page {info['page']}")

not_found = [r for r in missing if r not in found_rules]
if not_found:
    print(f"\nSTILL MISSING ({len(not_found)}): {not_found}")
