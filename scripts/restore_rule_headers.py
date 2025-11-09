#!/usr/bin/env python3
"""
Restore rule headers according to RULE_EXTRACTION_SCHEMA.md

The content should start with:
## § {N}. {Title}

Currently the title is just plain text. Need to add the header format.
"""

from pathlib import Path
import re
import yaml

def restore_rule_header(file_path):
    """Add back the ## § N. Title header to rule content"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split YAML frontmatter and content
    yaml_match = re.match(r'^---\n(.*?)\n---\n\n(.*)$', content, re.DOTALL)
    if not yaml_match:
        return False, "No YAML frontmatter found"

    yaml_text = yaml_match.group(1)
    body = yaml_match.group(2)

    # Parse YAML to get rule number
    try:
        metadata = yaml.safe_load(yaml_text)
        rule = metadata.get('rule', '')
        if not rule:
            return False, "No rule number in YAML"

        # Extract just the number from "§ 7" or "§ 7."
        rule_num = re.sub(r'§\s*(\d+)\.?', r'\1', rule)
    except Exception as e:
        return False, f"YAML parse error: {e}"

    # Check if header already exists
    if re.match(r'^## § \d+\.', body):
        return False, "Header already exists"

    # Get the first line as title (current format)
    first_line = body.split('\n')[0].strip()
    if not first_line:
        return False, "Empty content"

    # Check if first line is already a header of some kind
    if first_line.startswith('#'):
        return False, "Content starts with header already"

    # Create the proper header
    new_header = f"## § {rule_num}. {first_line}"

    # Replace first line with header
    lines = body.split('\n')
    lines[0] = new_header
    new_body = '\n'.join(lines)

    # Write back
    new_content = f"---\n{yaml_text}\n---\n\n{new_body}"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True, f"Added header: {new_header}"


# Process all rules
print("Restoring rule headers according to RULE_EXTRACTION_SCHEMA.md...\n")

fixed_count = 0
skipped_count = 0
error_count = 0

for rule_file in sorted(Path('phase3_rules').glob('rule_*.md')):
    success, message = restore_rule_header(rule_file)

    if success:
        print(f"✓ {rule_file.name}: {message}")
        fixed_count += 1
    elif "already exists" in message or "starts with header" in message:
        skipped_count += 1
    else:
        print(f"✗ {rule_file.name}: {message}")
        error_count += 1

print(f"\n{'='*60}")
print(f"Fixed: {fixed_count} rules")
print(f"Skipped (already have headers): {skipped_count} rules")
print(f"Errors: {error_count} rules")
print(f"{'='*60}")
