#!/usr/bin/env python3
"""
Fix footnote formatting in all rules to use standard markdown [^N] format.
Converts symbols (*, †, ‡, ×, §, ¶) to [^1], [^2], etc.

The key fix: Number footnotes based on order of first appearance in TEXT,
not based on order at bottom of file.
"""

import re
from pathlib import Path

def fix_footnotes_in_rule(file_path):
    """Fix footnote markers to use [^N] format based on text order"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into YAML and body
    yaml_match = re.match(r'^(---\n.*?\n---\n\n)(.*)$', content, re.DOTALL)
    if not yaml_match:
        return False, "No YAML found"

    yaml_section = yaml_match.group(1)
    body = yaml_match.group(2)

    # Footnote symbols
    footnote_symbols = ['*', '†', '‡', '×', '§', '¶', '**']

    # Find footnote definitions at bottom (lines starting with symbol + space)
    footnote_defs = {}  # symbol -> definition text
    lines = body.split('\n')

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Check if line starts with a footnote symbol
        for symbol in footnote_symbols:
            if stripped.startswith(symbol + ' '):
                text = stripped[len(symbol):].strip()
                footnote_defs[symbol] = text
                break

    if not footnote_defs:
        return False, "No footnotes with symbols found"

    # Find order of symbols in content (before footnote section)
    # We need to find where each symbol appears in the text
    symbol_order = []

    # Split body at the footnote separator (---) or find where footnotes start
    content_part = body
    footnote_section_start = len(body)

    # Find where footnote section starts (first line starting with symbol)
    for i, line in enumerate(lines):
        stripped = line.strip()
        for symbol in footnote_symbols:
            if stripped.startswith(symbol + ' '):
                # Found start of footnotes
                footnote_section_start = sum(len(l) + 1 for l in lines[:i])
                content_part = body[:footnote_section_start]
                break
        if footnote_section_start < len(body):
            break

    # Find symbols in content part in order of appearance
    for symbol in footnote_symbols:
        escaped = re.escape(symbol)
        # Find symbol in content (not at start of line which would be footnote def)
        # Look for symbol followed by space, semicolon, or end of word
        pattern = f'(?<!^){escaped}(?=\\s|;|$|\\.|,|\\))'
        matches = list(re.finditer(pattern, content_part, re.MULTILINE))
        if matches:
            # Record first position of this symbol
            first_pos = matches[0].start()
            symbol_order.append((first_pos, symbol))

    # Sort by position to get order of first appearance
    symbol_order.sort(key=lambda x: x[0])

    # Create symbol to number mapping based on text order
    symbol_to_num = {}
    for i, (pos, symbol) in enumerate(symbol_order, 1):
        symbol_to_num[symbol] = i

    # Also check if there are any symbols in footnote_defs that didn't appear in text
    # (this would be an error, but we should handle it)
    for symbol in footnote_defs:
        if symbol not in symbol_to_num:
            # This symbol has a definition but doesn't appear in text
            # Add it at the end
            symbol_to_num[symbol] = len(symbol_to_num) + 1

    if not symbol_to_num:
        return False, "No symbol mappings created"

    # Now rebuild the content
    new_lines = []
    in_footnote_section = False
    footnote_added = False

    for line in lines:
        stripped = line.strip()

        # Skip old footnote definition lines
        is_footnote_def = False
        for symbol in footnote_symbols:
            if stripped.startswith(symbol + ' '):
                is_footnote_def = True
                break

        if is_footnote_def:
            # Skip old footnote line, we'll add new ones later
            if not in_footnote_section:
                in_footnote_section = True
            continue

        # If we just entered footnote section, add separator and new footnotes
        if in_footnote_section and not footnote_added:
            # Add separator if not already present
            if new_lines and new_lines[-1].strip() != '---':
                new_lines.append('')
                new_lines.append('---')
            # Add markdown footnotes in correct order
            for num in sorted([n for s, n in symbol_to_num.items()]):
                # Find which symbol has this number
                for symbol, n in symbol_to_num.items():
                    if n == num and symbol in footnote_defs:
                        new_lines.append(f'[^{num}]: {footnote_defs[symbol]}')
                        break
            footnote_added = True
            continue

        # Replace symbols in content with [^N]
        modified_line = line
        for symbol, num in symbol_to_num.items():
            escaped = re.escape(symbol)
            # Replace symbol followed by space, semicolon, period, etc.
            modified_line = re.sub(f'{escaped}(?=\\s|;|$|\\.|,|\\))', f'[^{num}]', modified_line)

        new_lines.append(modified_line)

    # If footnotes weren't added yet (no footnote section found), add at end
    if symbol_to_num and not footnote_added:
        new_lines.append('')
        new_lines.append('---')
        for num in sorted([n for s, n in symbol_to_num.items()]):
            for symbol, n in symbol_to_num.items():
                if n == num and symbol in footnote_defs:
                    new_lines.append(f'[^{num}]: {footnote_defs[symbol]}')
                    break

    new_body = '\n'.join(new_lines)
    new_content = yaml_section + new_body

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True, f"Fixed {len(symbol_to_num)} footnotes"

# Process all rule files
print("Fixing footnotes in all phase3_rules...\n")

fixed_count = 0
skipped_count = 0
error_count = 0

for rule_file in sorted(Path('phase3_rules').glob('rule_*.md')):
    try:
        success, message = fix_footnotes_in_rule(rule_file)

        if success:
            print(f"✓ {rule_file.name}: {message}")
            fixed_count += 1
        elif "No footnotes" in message:
            skipped_count += 1
        else:
            print(f"  {rule_file.name}: {message}")
            skipped_count += 1
    except Exception as e:
        print(f"✗ {rule_file.name}: Error - {e}")
        error_count += 1

print(f"\n{'=' * 60}")
print(f"Fixed: {fixed_count} rules")
print(f"Skipped (no footnotes): {skipped_count} rules")
print(f"Errors: {error_count} rules")
print(f"{'=' * 60}")
