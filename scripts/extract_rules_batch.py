#!/usr/bin/env python3
"""
Extract rules in batches from phase2_cleaned pages to phase3_rules/core/raw/
Usage: python3 extract_rules_batch.py <start> <end>
"""

import re
import sys
import yaml
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path("/Users/skmnktl/Downloads/ocr")
CLEANED_DIR = BASE_DIR / "phase2_cleaned"
OUTPUT_DIR = BASE_DIR / "phase3_rules/core/raw"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def extract_rule_number(rule_str):
    """Extract numeric rule number from § N format"""
    match = re.search(r'§\s*(\d+)', str(rule_str))
    if match:
        return int(match.group(1))
    return None

def collect_rule_pages(start_rule, end_rule):
    """Scan all pages and collect which pages contain which rules"""
    rule_pages = defaultdict(list)

    for page_file in sorted(CLEANED_DIR.glob("page_*.md")):
        content = page_file.read_text(encoding='utf-8')
        yaml_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not yaml_match:
            continue

        try:
            metadata = yaml.safe_load(yaml_match.group(1))
        except:
            continue

        page_num = metadata.get('page_number')
        rules_starting = metadata.get('rules_starting', [])
        rules_continuing = metadata.get('rules_continuing', [])

        for rule in rules_starting:
            rule_num = extract_rule_number(rule)
            if rule_num and start_rule <= rule_num <= end_rule:
                rule_pages[rule_num].append({
                    'file': page_file,
                    'page_num': page_num,
                    'type': 'start'
                })

        for rule in rules_continuing:
            rule_num = extract_rule_number(rule)
            if rule_num and start_rule <= rule_num <= end_rule:
                rule_pages[rule_num].append({
                    'file': page_file,
                    'page_num': page_num,
                    'type': 'continue'
                })

    return rule_pages

def extract_rule_content(rule_num, pages_info):
    """Extract content for a specific rule from its pages"""
    pages_info = sorted(pages_info, key=lambda x: x['page_num'])

    all_content = []
    footnotes = []
    source_pages = []

    for page_info in pages_info:
        page_file = page_info['file']
        page_num = page_info['page_num']
        source_pages.append(f"{page_num:03d}")

        content = page_file.read_text(encoding='utf-8')
        parts = content.split('---', 2)
        if len(parts) < 3:
            continue

        body = parts[2].strip()

        if '## Footnotes' in body:
            body_parts = body.split('## Footnotes', 1)
            body = body_parts[0].strip()
            if len(body_parts) > 1:
                footnotes.append(body_parts[1].strip())

        if page_info['type'] == 'start':
            pattern = rf'§\s*{rule_num}\.\s*'
            match = re.search(pattern, body, re.MULTILINE)
            if match:
                start_pos = match.start()
                next_rule = re.search(r'\n§\s*\d+\.', body[start_pos + len(match.group(0)):])
                if next_rule:
                    end_pos = start_pos + len(match.group(0)) + next_rule.start()
                    all_content.append(body[start_pos:end_pos].strip())
                else:
                    all_content.append(body[start_pos:].strip())
        else:
            next_rule = re.search(r'\n§\s*\d+\.', body)
            if next_rule:
                all_content.append(body[:next_rule.start()].strip())
            else:
                all_content.append(body.strip())

    return {
        'content': '\n\n'.join(all_content),
        'footnotes': '\n\n'.join(footnotes),
        'source_pages': source_pages,
        'page_start': pages_info[0]['page_num'],
        'page_end': pages_info[-1]['page_num']
    }

def create_rule_file(rule_num, rule_data):
    """Create a rule_NNN.md file"""
    output_file = OUTPUT_DIR / f"rule_{rule_num:03d}.md"

    frontmatter = {
        'rule_number': rule_num,
        'rule_id': f"§ {rule_num}",
        'page_start': rule_data['page_start'],
        'page_end': rule_data['page_end'],
        'source_pages': rule_data['source_pages'],
        'extraction_status': 'raw'
    }

    content_parts = [
        '---',
        yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True).strip(),
        '---',
        '',
        rule_data['content']
    ]

    if rule_data['footnotes']:
        content_parts.extend(['', '---', '', '## Footnotes', '', rule_data['footnotes']])

    output_file.write_text('\n'.join(content_parts), encoding='utf-8')
    return output_file

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 extract_rules_batch.py <start> <end>")
        sys.exit(1)

    start_rule = int(sys.argv[1])
    end_rule = int(sys.argv[2])

    print(f"🚀 Extracting rules {start_rule}-{end_rule}...\n")

    rule_pages = collect_rule_pages(start_rule, end_rule)

    if not rule_pages:
        print(f"❌ No rules found in range {start_rule}-{end_rule}")
        return

    print(f"✓ Found {len(rule_pages)} rules\n")

    extracted = 0
    for rule_num in sorted(rule_pages.keys()):
        try:
            rule_data = extract_rule_content(rule_num, rule_pages[rule_num])
            output_file = create_rule_file(rule_num, rule_data)
            extracted += 1
            if extracted % 25 == 0:
                print(f"  ... {extracted} rules extracted")
        except Exception as e:
            print(f"❌ Rule {rule_num}: {e}")

    print(f"\n✅ Complete: extracted {extracted}/{len(rule_pages)} rules ({start_rule}-{end_rule})")

if __name__ == "__main__":
    main()
