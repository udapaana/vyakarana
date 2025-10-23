#!/usr/bin/env python3
"""
Use AI to identify section boundaries in v7

This script analyzes the v7 file and identifies:
- Chapter boundaries
- Section boundaries
- Rule (§) boundaries with their line numbers

Output: sections_index.json with structure like:
{
  "chapters": [
    {
      "number": "01",
      "title": "THE ALPHABET",
      "start_line": 200,
      "end_line": 410,
      "sections": [
        {
          "title": "alphabet_basics",
          "rules": [
            {"number": "1", "title": "Sanskrit or the refined language...", "start_line": 200, "end_line": 209},
            {"number": "2", "title": "The Devanāgarī alphabet...", "start_line": 210, "end_line": 243}
          ]
        }
      ]
    }
  ]
}
"""

import anthropic
import os
import json
from pathlib import Path

def analyze_document_structure(content: str, max_lines: int = 500) -> dict:
    """
    Use Claude to analyze document structure and identify section boundaries

    We'll process the document in chunks to stay within context limits
    """
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    lines = content.split('\n')

    prompt = f"""Analyze this Sanskrit grammar document and identify ALL section boundaries.

For each § rule, extract:
1. Rule number (the § number)
2. Line number where it starts
3. Rule title (text after §N.)
4. Chapter it belongs to
5. Section it belongs to (if any)

The document structure is:
- # Chapter I. (or II, III, etc.)
- ## SECTION NAME (like THE ALPHABET, RULES OF SANDHI)
- #### § 1. Rule title and content...

Here are the first {max_lines} lines (with line numbers):

"""

    # Add line numbers to first chunk
    numbered_lines = []
    for i, line in enumerate(lines[:max_lines], 1):
        numbered_lines.append(f"{i:4d}: {line}")

    prompt += '\n'.join(numbered_lines)

    prompt += """

Please output a JSON structure identifying:
1. All chapters with their start lines
2. All sections with their start lines
3. All § rules with their numbers, titles, and start lines

Format:
{
  "chapters": [
    {
      "number": "I",
      "title": "THE ALPHABET",
      "start_line": 200,
      "sections": [
        {
          "title": "alphabet_basics",
          "start_line": 200,
          "rules": [
            {"number": "1", "title": "Sanskrit or refined language", "start_line": 200},
            {"number": "2", "title": "Devanāgarī alphabet", "start_line": 210}
          ]
        }
      ]
    }
  ]
}

Only output valid JSON, nothing else."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )

    # Parse response
    json_text = response.content[0].text
    # Extract JSON if wrapped in markdown
    if '```json' in json_text:
        json_text = json_text.split('```json')[1].split('```')[0]
    elif '```' in json_text:
        json_text = json_text.split('```')[1].split('```')[0]

    return json.loads(json_text.strip())

def scan_full_document(file_path: Path) -> dict:
    """
    Scan the full document by processing it in overlapping chunks
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    total_lines = len(lines)

    print(f"📖 Document has {total_lines} lines")
    print(f"🔍 Analyzing structure with AI...\n")

    # For now, let's do a simpler approach:
    # 1. First pass: identify all § markers with grep-like scanning
    # 2. Second pass: use AI to classify and organize them

    rules = []
    current_chapter = None
    current_section = None

    for i, line in enumerate(lines, 1):
        # Detect chapter (both "Chapter" and "CHAPTER")
        if line.strip().startswith('# Chapter') or line.strip().startswith('# CHAPTER'):
            import re
            match = re.search(r'[Cc][Hh][Aa][Pp][Tt][Ee][Rr]\s+([IVX]+)', line)
            if match:
                current_chapter = {
                    'number': match.group(1),
                    'title': '',
                    'start_line': i,
                    'sections': []
                }
                print(f"📂 Chapter {current_chapter['number']} at line {i}")

        # Detect section (## or ### heading after chapter, but not ####)
        elif current_chapter and (line.strip().startswith('###') or line.strip().startswith('##')) and not line.strip().startswith('####'):
            title = line.strip('#').strip()
            current_section = {
                'title': title,
                'start_line': i,
                'rules': []
            }
            if current_chapter and 'sections' in current_chapter:
                current_chapter['sections'].append(current_section)
            print(f"   📁 Section: {title[:50]}... at line {i}")

        # Detect rule (#### §)
        elif line.strip().startswith('#### §'):
            import re
            match = re.match(r'####\s*§\s*(\d+)\.\s*(.*)', line.strip())
            if match:
                rule = {
                    'number': match.group(1),
                    'title': match.group(2).strip(),
                    'start_line': i
                }
                if current_section:
                    current_section['rules'].append(rule)
                else:
                    rules.append(rule)  # Orphan rule

                if int(rule['number']) % 10 == 0:  # Print every 10th
                    print(f"      ✅ §{rule['number']} at line {i}")

    # Build final structure
    # We need to collect all chapters
    chapters = []
    current_chapter = None
    current_section = None

    for i, line in enumerate(lines, 1):
        if line.strip().startswith('# Chapter') or line.strip().startswith('# CHAPTER'):
            import re
            match = re.search(r'[Cc][Hh][Aa][Pp][Tt][Ee][Rr]\s+([IVX]+)', line)
            if match:
                # Save previous section and chapter
                if current_section and current_section.get('rules'):
                    current_chapter['sections'].append(current_section)
                if current_chapter:
                    chapters.append(current_chapter)
                # Start new chapter
                current_chapter = {
                    'number': match.group(1),
                    'title': '',
                    'start_line': i,
                    'sections': []
                }
                current_section = None

        elif current_chapter and (line.strip().startswith('###') or line.strip().startswith('##')) and not line.strip().startswith('####'):
            title = line.strip('#').strip()
            if current_section and current_section['rules']:
                current_chapter['sections'].append(current_section)
            current_section = {
                'title': title,
                'start_line': i,
                'rules': []
            }

        elif line.strip().startswith('#### §'):
            import re
            match = re.match(r'####\s*§\s*(\d+)\.\s*(.*)', line.strip())
            if match:
                rule = {
                    'number': match.group(1),
                    'title': match.group(2).strip(),
                    'start_line': i
                }
                # If we have a rule but no section, create a default section
                if current_section is None and current_chapter:
                    current_section = {
                        'title': f'{current_chapter["number"]}. (Rules without section header)',
                        'start_line': i,
                        'rules': []
                    }
                if current_section is not None:
                    current_section['rules'].append(rule)

    # Add last section and chapter
    if current_section and current_section['rules']:
        current_chapter['sections'].append(current_section)
    if current_chapter:
        chapters.append(current_chapter)

    return {'chapters': chapters}

def main():
    project_root = Path(__file__).parent.parent.parent
    v7_file = project_root / "output" / "kales_sanskrit_grammar_v7.md"
    output_file = project_root / "sections_index.json"

    if not v7_file.exists():
        print(f"❌ Error: v7 file not found at {v7_file}")
        return

    # Scan document
    structure = scan_full_document(v7_file)

    # Save to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Structure analysis complete!")
    print(f"   Output: {output_file}")

    # Print summary
    total_rules = sum(
        len(section['rules'])
        for chapter in structure['chapters']
        for section in chapter.get('sections', [])
    )
    print(f"\n📊 Summary:")
    print(f"   Chapters: {len(structure['chapters'])}")
    print(f"   Total rules: {total_rules}")

if __name__ == "__main__":
    main()
