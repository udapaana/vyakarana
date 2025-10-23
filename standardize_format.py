#!/usr/bin/env python3
"""
Comprehensive standardization and cleanup of kales_sanskrit_grammar_complete.md

Goals:
1. Standardize Sanskrit notation with @[...] tags
2. Convert all Sanskrit to proper IAST transliteration
3. Fix broken paragraphs
4. Remove page markers and artifacts
5. Improve markdown structure
6. Standardize capitalization
"""

import re
from typing import List, Tuple

# Common Sanskrit grammatical terms that should be tagged
SANSKRIT_TERMS = [
    'sandhi', 'samasa', 'guna', 'vrddhi', 'krit', 'taddhita',
    'pratyaya', 'dhatu', 'vibhakti', 'sutra', 'pada', 'samhita',
    'svarasandhi', 'halsandhi', 'visargasandhi', 'subanta', 'tinganta',
    'parasmaipada', 'atmanepada', 'lakara', 'prakriya', 'samdhi',
    'samavrttas', 'visama', 'vrttas', 'pluta', 'pragrihya',
    'karaka', 'samjna', 'paribhasa', 'adhikara', 'anuvritta'
]

# Sanskrit words with proper IAST that are commonly capitalized
SANSKRIT_PROPER_NOUNS = {
    'PANINI': 'Pāṇini',
    'PATANJALI': 'Patañjali',
    'KATYAYANA': 'Kātyāyana',
    'VOPADEVA': 'Vopadeva',
    'BHATTOJI': 'Bhaṭṭoji',
    'KALIDASA': 'Kālidāsa',
    'BHARTRHARI': 'Bhartṛhari',
}

def fix_broken_paragraphs(lines: List[str]) -> List[str]:
    """
    Join broken paragraphs that should be continuous.
    Keep intentional line breaks (headings, lists, etc.)
    """
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Keep headings, blank lines, and list items as-is
        if (line.startswith('#') or
            not line.strip() or
            re.match(r'^\s*[-•*]\s', line) or
            re.match(r'^\s*\(\d+\)', line) or
            re.match(r'^\s*\d+\.', line)):
            result.append(line)
            i += 1
            continue

        # If current line doesn't end with punctuation and next line exists and is not special
        if (line.strip() and
            not re.search(r'[.,:;?!—…]$', line.strip()) and
            i + 1 < len(lines) and
            lines[i + 1].strip() and
            not lines[i + 1].startswith('#') and
            not re.match(r'^\s*[-•*\(]', lines[i + 1]) and
            len(line.strip()) > 40):  # Don't join very short lines

            # Join with next line
            combined = line.rstrip() + ' ' + lines[i + 1].lstrip()
            result.append(combined)
            i += 2
        else:
            result.append(line)
            i += 1

    return result

def remove_page_markers(text: str) -> str:
    """Remove page number markers like '... 123'"""
    # Remove patterns like "... ... 123" or "... 123"
    text = re.sub(r'\s*\.{2,}\s+\d+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s+\d+\s*$', lambda m: '' if len(m.group()) < 6 else m.group(), text, flags=re.MULTILINE)
    return text

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

def standardize_all_caps_headings(text: str) -> str:
    """Convert ALL CAPS headings to proper markdown headings"""
    lines = text.split('\n')
    result = []

    for line in lines:
        stripped = line.strip()

        # Skip if already a heading
        if line.startswith('#'):
            result.append(line)
            continue

        # Detect all-caps lines that should be headings
        if (len(stripped) > 10 and
            stripped.isupper() and
            not re.search(r'@\[', stripped)):  # Not already tagged Sanskrit

            # Determine heading level based on content
            if any(word in stripped for word in ['CHAPTER', 'APPENDIX']):
                result.append(f"# {stripped.title()}")
            elif any(word in stripped for word in ['SECTION', 'PART']):
                result.append(f"## {stripped.title()}")
            else:
                result.append(f"### {stripped.title()}")
        else:
            result.append(line)

    return '\n'.join(result)

def tag_common_sanskrit_terms(text: str) -> str:
    """Tag common Sanskrit grammatical terms that aren't already tagged"""
    for term in SANSKRIT_TERMS:
        # Match whole word, case-insensitive, not already in @[...]
        pattern = rf'\b({term})\b(?![^\[]*\])'

        def replace_if_not_tagged(match):
            word = match.group(1)
            # Check if already inside @[...]
            start = match.start()
            # Look backwards for @[ and forwards for ]
            before = text[max(0, start-50):start]
            after = text[start:min(len(text), start+50)]

            if '@[' in before and ']' not in before.split('@[')[-1]:
                return word  # Already inside a tag

            return f'@[{word}]'

        text = re.sub(pattern, replace_if_not_tagged, text, flags=re.IGNORECASE)

    return text

def standardize_sanskrit_capitalization(text: str) -> str:
    """
    Standardize Sanskrit proper nouns to proper IAST.
    Keep pedagogical capitals where appropriate (e.g., technical terms in explanations)
    """
    for wrong, correct in SANSKRIT_PROPER_NOUNS.items():
        # Replace all-caps versions
        text = re.sub(rf'\b{wrong}\b', correct, text)
        # Also fix common variations
        text = re.sub(rf'\b{wrong.title()}\b', correct, text)

    return text

def fix_table_of_contents(text: str) -> str:
    """
    Improve table of contents formatting.
    Lines with "CHAPTER" and page numbers should be properly structured.
    """
    lines = text.split('\n')
    result = []
    in_toc = False

    for line in lines:
        # Detect TOC section
        if 'CHAPTER' in line and 'PAGE' in line.upper():
            in_toc = True
            result.append('## Table of Contents\n')
            continue

        # End of TOC detection
        if in_toc and line.startswith('#'):
            in_toc = False

        if in_toc and line.strip():
            # Format TOC entries
            # Remove excessive spacing
            line = re.sub(r'\s{2,}', ' ', line)
            result.append(line)
        else:
            result.append(line)

    return '\n'.join(result)

def improve_section_structure(text: str) -> str:
    """
    Improve section markers like § 1., § 2. to be consistent h4 headings
    """
    # Ensure § markers are h4 headings
    text = re.sub(r'^(§+\s*\d+[.\-\d]*)\s+', r'#### \1 ', text, flags=re.MULTILINE)

    # Ensure Roman numeral sections are h3
    text = re.sub(r'^([IVX]+\.\s+[A-Z@])', r'### \1', text, flags=re.MULTILINE)

    return text

def main():
    input_file = 'kales_sanskrit_grammar_complete.md'
    output_file = 'kales_sanskrit_grammar_standardized.md'

    print("Reading input file...")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    print("Step 1: Removing page markers...")
    content = remove_page_markers(content)

    print("Step 2: Standardizing all-caps headings...")
    content = standardize_all_caps_headings(content)

    print("Step 3: Fixing table of contents...")
    content = fix_table_of_contents(content)

    print("Step 4: Improving section structure...")
    content = improve_section_structure(content)

    print("Step 5: Standardizing Sanskrit capitalization...")
    content = standardize_sanskrit_capitalization(content)

    print("Step 6: Tagging common Sanskrit terms...")
    content = tag_common_sanskrit_terms(content)

    print("Step 7: Fixing broken paragraphs...")
    lines = content.split('\n')
    lines = fix_broken_paragraphs(lines)

    print("Step 8: Removing multiple blank lines...")
    lines = remove_multiple_blanks(lines)

    content = '\n'.join(lines)

    print(f"Writing output to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ Standardization complete!")
    print(f"Output: {output_file}")

    # Print statistics
    original_lines = len(open(input_file).readlines())
    new_lines = len(open(output_file).readlines())

    print(f"\nStatistics:")
    print(f"  Original lines: {original_lines}")
    print(f"  New lines: {new_lines}")
    print(f"  Difference: {original_lines - new_lines} lines removed")

if __name__ == '__main__':
    main()
