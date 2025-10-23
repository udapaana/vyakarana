#!/usr/bin/env python3
"""
Improved comprehensive standardization of kales_sanskrit_grammar_complete.md

This version is more careful about:
1. Not joining TOC lines
2. Better Sanskrit term detection
3. Preserving pedagogical formatting
4. Better handling of tables and lists
"""

import re
from typing import List, Tuple

# Common Sanskrit grammatical terms that should be tagged
SANSKRIT_TERMS = [
    'sandhi', 'samasa', 'guna', 'vrddhi', 'krit', 'taddhita',
    'pratyaya', 'dhatu', 'vibhakti', 'sutra', 'pada', 'samhita',
    'svarasandhi', 'halsandhi', 'visargasandhi', 'subanta', 'tinganta',
    'parasmaipada', 'atmanepada', 'lakara', 'prakriya',
    'samavrttas', 'visama', 'vrttas', 'pluta', 'pragrihya',
    'karaka', 'samjna', 'paribhasa', 'adhikara', 'anuvritta'
]

def is_toc_line(line: str) -> bool:
    """Check if line is part of table of contents"""
    # TOC lines typically have chapter/section markers and page numbers at end
    if re.match(r'^\s*\d+\s+', line):  # Starts with number
        return True
    if re.search(r'\.\.\.\s*$', line):  # Ends with dots (TOC page marker)
        return True
    if re.match(r'^\s*\([a-z]\)\s+', line):  # Starts with (a), (b), etc
        return True
    if re.search(r'\s+\d{1,3}\s*$', line) and len(line.strip()) < 80:  # Ends with page number
        return True
    return False

def fix_broken_paragraphs(lines: List[str]) -> List[str]:
    """
    Join broken paragraphs intelligently.
    Be very careful not to join:
    - TOC entries
    - Headings
    - Lists
    - Tables
    - Sanskrit examples
    """
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Keep headings, blank lines, and special formats as-is
        if (line.startswith('#') or
            not line.strip() or
            re.match(r'^\s*[-•*]\s', line) or
            re.match(r'^\s*\(\d+\)', line) or
            re.match(r'^\s*\d+\.', line) or
            re.match(r'^---+', line) or  # Horizontal rules
            is_toc_line(line)):
            result.append(line)
            i += 1
            continue

        # Check if next line exists and can be joined
        if i + 1 < len(lines):
            next_line = lines[i + 1]

            # Don't join if current line looks complete
            ends_with_punctuation = re.search(r'[.,:;?!—…]$', line.strip())

            # Don't join if next line is special
            next_is_special = (next_line.startswith('#') or
                             not next_line.strip() or
                             re.match(r'^\s*[-•*\(]', next_line) or
                             is_toc_line(next_line))

            # Don't join very short lines (likely formatting)
            too_short = len(line.strip()) < 40

            # Don't join if line contains Sanskrit examples (lots of @[...])
            has_many_tags = line.count('@[') >= 3

            if (not ends_with_punctuation and
                not next_is_special and
                not too_short and
                not has_many_tags and
                next_line.strip()):

                # Join with next line
                combined = line.rstrip() + ' ' + next_line.lstrip()
                result.append(combined)
                i += 2
            else:
                result.append(line)
                i += 1
        else:
            result.append(line)
            i += 1

    return result

def remove_page_markers(text: str) -> str:
    """
    Remove page number markers like '... ... 123' more carefully.
    Preserve page numbers that are part of citations or examples.
    """
    lines = text.split('\n')
    result = []

    for line in lines:
        # Remove TOC-style page markers: "... ... 123" or "... 123"
        if is_toc_line(line):
            # Keep TOC lines but clean them up
            line = re.sub(r'\s*\.{2,}\s+(\d+)\s*$', r' - \1', line)
        else:
            # For non-TOC lines, remove trailing page numbers more conservatively
            # Only if line ends with dots and a number
            line = re.sub(r'\s*\.{2,}\s+\d+\s*$', '', line)

        result.append(line)

    return '\n'.join(result)

def remove_multiple_blanks(lines: List[str]) -> List[str]:
    """Reduce multiple consecutive blank lines to max 2"""
    result = []
    blank_count = 0

    for line in lines:
        if not line.strip():
            blank_count += 1
            if blank_count <= 2:
                result.append(line)
        else:
            blank_count = 0
            result.append(line)

    return result

def standardize_headings(text: str) -> str:
    """
    Convert improperly formatted headings to proper markdown.
    Be conservative - only fix obvious cases.
    """
    lines = text.split('\n')
    result = []

    for line in lines:
        stripped = line.strip()

        # Skip if already a heading
        if line.startswith('#'):
            result.append(line)
            continue

        # Detect all-caps section headings (but not TOC lines)
        if (len(stripped) > 10 and
            len(stripped) < 100 and  # Not too long
            stripped.isupper() and
            not re.search(r'@\[', stripped) and  # Not tagged Sanskrit
            not is_toc_line(line) and
            not re.search(r'\d{2,}', stripped)):  # No multi-digit numbers (likely page refs)

            # Determine heading level based on content
            if any(word in stripped for word in ['CHAPTER', 'APPENDIX', 'PREFACE']):
                result.append(f"# {stripped.title()}")
            elif any(word in stripped for word in ['SECTION', 'PART']):
                result.append(f"## {stripped.title()}")
            else:
                # Check if it looks like a major section heading
                if len(stripped.split()) <= 5:  # Short titles
                    result.append(f"## {stripped.title()}")
                else:
                    result.append(f"### {stripped.title()}")
        else:
            result.append(line)

    return '\n'.join(result)

def tag_sanskrit_terms(text: str) -> str:
    """
    Tag common Sanskrit grammatical terms.
    Be careful not to double-tag or break existing formatting.
    """
    for term in SANSKRIT_TERMS:
        # Only tag if not already tagged and not in a heading
        # Match whole word, case-insensitive
        pattern = rf'(?<!@\[)\b({term})\b(?![^\[]*\])'

        def replace_func(match):
            word = match.group(1)
            # Don't tag if in heading
            line_start = text.rfind('\n', 0, match.start()) + 1
            line_end = text.find('\n', match.end())
            if line_end == -1:
                line_end = len(text)
            line = text[line_start:line_end]

            if line.strip().startswith('#'):
                return word

            # Don't tag if already inside @[...]
            before_context = text[max(0, match.start()-100):match.start()]
            if '@[' in before_context and ']' not in before_context.split('@[')[-1]:
                return word

            return f'@[{word}]'

        text = re.sub(pattern, replace_func, text, flags=re.IGNORECASE)

    return text

def improve_section_structure(text: str) -> str:
    """
    Ensure § section markers are properly formatted as headings.
    Ensure Roman numeral sections are headings.
    """
    lines = text.split('\n')
    result = []

    for line in lines:
        stripped = line.strip()

        # § markers should be h4 headings
        if re.match(r'^§+\s*\d+', stripped) and not line.startswith('#'):
            result.append(f"#### {stripped}")
        # Roman numeral sections should be h3
        elif re.match(r'^[IVX]+\.\s+[A-Z@]', stripped) and not line.startswith('#'):
            result.append(f"### {stripped}")
        else:
            result.append(line)

    return '\n'.join(result)

def format_toc(text: str) -> str:
    """Format table of contents more cleanly"""
    lines = text.split('\n')
    result = []
    in_toc = False
    toc_started = False

    for i, line in enumerate(lines):
        # Detect start of TOC
        if ('CONTENTS' in line.upper() or
            (re.match(r'^\s*#*\s*Chapter', line, re.IGNORECASE) and
             i + 1 < len(lines) and 'Page' in lines[i+1])):
            if not toc_started:
                result.append('\n## Table of Contents\n')
                toc_started = True
                in_toc = True
            continue

        # Detect end of TOC (usually when we hit "PREFACE" or first real heading)
        if in_toc and (line.startswith('# ') and 'Chapter' not in line):
            in_toc = False

        if in_toc and line.strip():
            # Clean up TOC entry
            cleaned = re.sub(r'\s{3,}', ' ', line)  # Multiple spaces to single
            cleaned = re.sub(r'\s*\.{2,}\s*', ' - ', cleaned)  # Dots to dash
            result.append(cleaned)
        else:
            result.append(line)

    return '\n'.join(result)

def main():
    input_file = 'kales_sanskrit_grammar_complete.md'
    output_file = 'kales_sanskrit_grammar_standardized_v2.md'

    print("📖 Reading input file...")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    original_length = len(content)

    print("🧹 Step 1: Removing page markers...")
    content = remove_page_markers(content)

    print("📝 Step 2: Standardizing headings...")
    content = standardize_headings(content)

    print("📋 Step 3: Formatting table of contents...")
    content = format_toc(content)

    print("🔢 Step 4: Improving section structure...")
    content = improve_section_structure(content)

    print("🏷️  Step 5: Tagging Sanskrit terms...")
    content = tag_sanskrit_terms(content)

    print("📄 Step 6: Fixing broken paragraphs...")
    lines = content.split('\n')
    lines = fix_broken_paragraphs(lines)

    print("⬜ Step 7: Removing multiple blank lines...")
    lines = remove_multiple_blanks(lines)

    content = '\n'.join(lines)

    print(f"💾 Writing output to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    new_length = len(content)

    print("\n✅ Standardization complete!")
    print(f"\n📊 Statistics:")
    print(f"  Input:  {input_file}")
    print(f"  Output: {output_file}")
    print(f"  Original size: {original_length:,} bytes")
    print(f"  New size: {new_length:,} bytes")
    print(f"  Reduction: {original_length - new_length:,} bytes ({100*(original_length-new_length)/original_length:.1f}%)")

    # Count improvements
    with open(input_file) as f:
        original_lines = f.readlines()
    with open(output_file) as f:
        new_lines = f.readlines()

    print(f"  Original lines: {len(original_lines):,}")
    print(f"  New lines: {len(new_lines):,}")
    print(f"  Lines removed: {len(original_lines) - len(new_lines):,}")

if __name__ == '__main__':
    main()
