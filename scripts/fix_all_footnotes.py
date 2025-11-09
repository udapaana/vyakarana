#!/usr/bin/env python3
"""
Fix footnote formatting in all rules to use standard markdown [^N] format.
Converts symbols (*, †, ‡, ×, §) to [^1], [^2], etc.
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

    # Find lines at bottom that start with footnote symbols
    # Pattern: starts with *, †, ‡, ×, §, ¶ at beginning of line
    footnote_symbols = ['*', '†', '‡', '×', '§', '¶']

    # Split body into lines
    lines = body.split('\n')

    # Find footnote section (after --- separator or at end)
    footnote_lines = []
    content_lines = []
    in_footnote_section = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        # Check if this is a footnote definition line
        if stripped and stripped[0] in footnote_symbols and ' ' in stripped:
            in_footnote_section = True
            symbol = stripped[0]
            text = stripped[2:].strip() if len(stripped) > 2 else stripped[1:].strip()
            footnote_lines.append((symbol, text, i))
        elif stripped == '---' and in_footnote_section:
            # Separator before footnotes
            content_lines.append(i)
        elif not in_footnote_section or (in_footnote_section and not stripped.startswith(tuple(footnote_symbols))):
            content_lines.append(i)

    if not footnote_lines:
        return False, "No footnotes with symbols found"

    # Create symbol to number mapping
    symbol_to_num = {}
    footnote_map = {}
    for i, (symbol, text, line_idx) in enumerate(footnote_lines, 1):
        if symbol not in symbol_to_num:
            symbol_to_num[symbol] = i
        footnote_map[i] = text

    # Rebuild content
    new_body_parts = []
    footnote_section_started = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip old footnote lines
        if any(line_idx == i for _, _, line_idx in footnote_lines):
            continue

        # Check if this is separator before footnotes
        if stripped == '---' and i < len(lines) - 5:
            # Check if footnotes follow
            has_footnotes_after = any(line_idx > i for _, _, line_idx in footnote_lines)
            if has_footnotes_after and not footnote_section_started:
                new_body_parts.append(line)
                footnote_section_started = True
                # Add new markdown footnotes
                for num in sorted(footnote_map.keys()):
                    new_body_parts.append(f'[^{num}]: {footnote_map[num]}')
                continue

        # Replace symbols in content with [^N]
        modified_line = line
        for symbol, num in symbol_to_num.items():
            # Replace symbol at end of sentence or before space/semicolon
            escaped_symbol = re.escape(symbol)
            # Common patterns: "text;* e.g." or "text*;" or "text* "
            modified_line = re.sub(f'{escaped_symbol}(?=\\s|;|$|e\\.g\\.)', f'[^{num}]', modified_line)

        new_body_parts.append(modified_line)

    # If footnotes weren't added yet (no --- separator), add them at end
    if not footnote_section_started and footnote_map:
        new_body_parts.append('')
        new_body_parts.append('---')
        new_body_parts.append('')
        for num in sorted(footnote_map.keys()):
            new_body_parts.append(f'[^{num}]: {footnote_map[num]}')

    new_body = '\n'.join(new_body_parts)
    new_content = yaml_section + new_body

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True, f"Fixed {len(footnote_map)} footnotes"

# Process all rule files
print("Fixing footnotes in all phase3_rules...\n")

fixed_count = 0
skipped_count = 0
error_count = 0

for rule_file in sorted(Path('phase3_rules').glob('rule_*.md')):
    success, message = fix_footnotes_in_rule(rule_file)

    if success:
        print(f"✓ {rule_file.name}: {message}")
        fixed_count += 1
    elif "No footnotes" in message:
        skipped_count += 1
    else:
        print(f"✗ {rule_file.name}: {message}")
        error_count += 1

print(f"\n{'=' * 60}")
print(f"Fixed: {fixed_count} rules")
print(f"Skipped (no footnotes): {skipped_count} rules")
print(f"Errors: {error_count} rules")
print(f"{'=' * 60}")
