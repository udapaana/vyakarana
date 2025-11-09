#!/usr/bin/env python3
"""
Fix footnote formatting in rules 39-45
Convert symbols (*, †, ‡, ×, §) to markdown footnote references [^1], [^2], etc.
"""

import re
from pathlib import Path

def fix_footnotes_in_rule(file_path):
    """Fix footnote markers to use [^N] format"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into YAML and body
    yaml_match = re.match(r'^(---\n.*?\n---\n\n)(.*)$', content, re.DOTALL)
    if not yaml_match:
        return False, "No YAML found"

    yaml_section = yaml_match.group(1)
    body = yaml_match.group(2)

    # Map symbols to footnote numbers
    # Common pattern: symbol in text, then symbol at bottom with Pāṇini reference

    # Find all footnote markers at the bottom (lines starting with symbols)
    footnote_pattern = r'^([*†‡×§¶]) (.+)$'
    footnotes_at_bottom = []
    for line in body.split('\n'):
        match = re.match(footnote_pattern, line.strip())
        if match:
            footnotes_at_bottom.append((match.group(1), match.group(2).strip()))

    if not footnotes_at_bottom:
        return False, "No footnotes found"

    # Create mapping of symbol to number
    symbol_to_num = {}
    for i, (symbol, text) in enumerate(footnotes_at_bottom, 1):
        symbol_to_num[symbol] = i

    # Replace symbols in content with [^N]
    for symbol, num in symbol_to_num.items():
        # Escape special regex characters
        escaped_symbol = re.escape(symbol)
        # Replace symbol followed by space or semicolon
        body = re.sub(f'{escaped_symbol}(?=\\s|;)', f'[^{num}]', body)

    # Replace footnotes at bottom with [^N]: format
    for symbol, num in symbol_to_num.items():
        escaped_symbol = re.escape(symbol)
        body = re.sub(f'^{escaped_symbol} (.+)$', f'[^{num}]: \\1', body, flags=re.MULTILINE)

    # Write back
    new_content = yaml_section + body
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True, f"Fixed {len(symbol_to_num)} footnotes"

# Process rules 39-45
print("Fixing footnotes in rules 39-45...\n")

for i in range(39, 46):
    rule_file = Path(f'phase3_rules/rule_{i:03d}.md')
    if not rule_file.exists():
        print(f"Rule {i}: Not found")
        continue

    success, message = fix_footnotes_in_rule(rule_file)
    if success:
        print(f"✓ Rule {i}: {message}")
    else:
        print(f"  Rule {i}: {message}")

print("\nDone!")
