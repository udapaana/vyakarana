#!/usr/bin/env python3
"""
Analyze formatting issues in kales_sanskrit_grammar_complete.md
"""

import re
from collections import defaultdict

def analyze_formatting_issues(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    issues = defaultdict(list)

    for i, line in enumerate(lines, 1):
        # 1. Untagged Sanskrit words (capitalized non-English words)
        # Look for capitalized words that might be Sanskrit but aren't tagged
        untagged_sanskrit = re.findall(r'\b[A-Z][a-z]*[āīūṛṃḥñṭḍṇśṣ][a-z]*\b', line)
        if untagged_sanskrit and not line.startswith('#'):
            issues['untagged_sanskrit'].append((i, line[:100], untagged_sanskrit))

        # 2. All-caps sections (potential headings or page markers)
        if re.match(r'^[A-Z\s]{10,}', line.strip()) and not line.startswith('#'):
            issues['all_caps_lines'].append((i, line[:100]))

        # 3. Page markers that might remain
        if re.search(r'\.\.\.\s+\d+\s*$', line):
            issues['page_markers'].append((i, line[:100]))

        # 4. Broken paragraphs (single lines ending without punctuation)
        if line.strip() and not line.startswith('#') and not line.startswith('-'):
            if not re.search(r'[.,:;?!—]$', line.strip()) and len(line.strip()) > 40:
                if i < len(lines) and lines[i].strip() and not lines[i].startswith('#'):
                    issues['broken_paragraphs'].append((i, line[:100]))

        # 5. Multiple consecutive blank lines
        if i > 2 and not line.strip() and not lines[i-2].strip():
            issues['multiple_blanks'].append((i, "multiple blank lines"))

        # 6. Inconsistent Sanskrit notation (mixed @[...] and plain text)
        sanskrit_words = ['guna', 'vrddhi', 'sandhi', 'samasa', 'krit', 'taddhita',
                         'sutra', 'pratyaya', 'dhatu', 'vibhakti']
        for word in sanskrit_words:
            # Check for untagged common Sanskrit terms
            if re.search(rf'\b{word}\b', line, re.IGNORECASE):
                if f'@[{word}]' not in line.lower():
                    issues['untagged_common_terms'].append((i, line[:100], word))

    return issues

def print_analysis(issues):
    print("=" * 80)
    print("FORMATTING ISSUES ANALYSIS")
    print("=" * 80)

    for issue_type, occurrences in sorted(issues.items()):
        print(f"\n{'=' * 80}")
        print(f"{issue_type.upper().replace('_', ' ')}: {len(occurrences)} occurrences")
        print(f"{'=' * 80}")

        # Show first 10 examples
        for i, occ in enumerate(occurrences[:10], 1):
            if len(occ) == 2:
                line_num, text = occ
                print(f"{i}. Line {line_num}: {text}")
            elif len(occ) == 3:
                line_num, text, extra = occ
                print(f"{i}. Line {line_num}: {text}")
                print(f"   → Found: {extra}")

        if len(occurrences) > 10:
            print(f"\n... and {len(occurrences) - 10} more")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    for issue_type, occurrences in sorted(issues.items()):
        print(f"{issue_type.replace('_', ' ').title()}: {len(occurrences)}")

if __name__ == '__main__':
    issues = analyze_formatting_issues('kales_sanskrit_grammar_complete.md')
    print_analysis(issues)
