#!/usr/bin/env python3
"""
Process rules through Claude API for cleanup.
Handles OCR corrections, IAST standardization, and markdown formatting.
"""

import json
from pathlib import Path
import sys
import os

MARKDOWN_SPEC_FILE = Path('MARKDOWN_SPEC.md')
RULES_DIR = Path('rules')
OUTPUT_DIR = Path('rules_cleaned')
PROGRESS_FILE = Path('cleanup_progress.json')

def load_progress():
    """Load processing progress"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {'completed': [], 'failed': [], 'skipped': []}

def save_progress(progress):
    """Save processing progress"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def get_cleanup_prompt(spec_content):
    """Generate the cleanup prompt"""
    return f"""You are cleaning up an OCR-extracted rule from Kale's Sanskrit Grammar.

**Your tasks:**
1. Fix OCR errors (misread characters, wrong digits, spacing issues)
2. Fix typos and grammatical errors in English text
3. Standardize all romanized Sanskrit to proper IAST notation wrapped in @[...]
4. Wrap all Devanagari text in @deva[...]
5. Remove any rule number headers (like #### § N.) from the content - the rule number is already in YAML
6. Ensure proper markdown formatting per specification
7. Fix spacing and paragraph breaks

**CRITICAL RULES:**
- Do NOT change the meaning or content
- Do NOT translate anything
- Do NOT remove examples, notes, or references
- Maintain the YAML front matter exactly as is
- IAST in @[...], Devanagari in @deva[...]
- Use proper IAST diacriticals (ā, ī, ū, ṛ, ṃ, ḥ, ś, ṣ, ṇ, ṭ, ḍ, etc.)
- Maintain standard capitalization (not all lowercase)

Return ONLY the cleaned markdown content (including YAML front matter). No explanations or comments.

**Specification:**

{spec_content}"""

def process_rule_with_claude(rule_num, spec_prompt):
    """Process a single rule using Claude API"""
    filename = f"{rule_num:03d}.md"
    input_path = RULES_DIR / filename
    output_path = OUTPUT_DIR / filename

    if not input_path.exists():
        return None, "File not found"

    # Read input
    content = input_path.read_text(encoding='utf-8')

    # Skip placeholders
    if 'DOES NOT EXIST IN ORIGINAL' in content:
        OUTPUT_DIR.mkdir(exist_ok=True)
        output_path.write_text(content, encoding='utf-8')
        return 'skipped', 'Placeholder file'

    # Create full prompt
    full_prompt = f"{spec_prompt}\n\n**Rule to clean:**\n\n{content}"

    try:
        import anthropic

        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return None, "ANTHROPIC_API_KEY not set"

        client = anthropic.Anthropic(api_key=api_key)

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": full_prompt}]
        )

        cleaned_content = message.content[0].text

        # Save output
        OUTPUT_DIR.mkdir(exist_ok=True)
        output_path.write_text(cleaned_content, encoding='utf-8')

        return 'success', 'Cleaned successfully'

    except Exception as e:
        return 'failed', str(e)

def process_batch(start, end, spec_prompt):
    """Process a batch of rules"""
    progress = load_progress()

    print("="*60)
    print(f"Processing rules §{start} to §{end}")
    print("="*60)

    success = 0
    failed = 0
    skipped = 0

    for rule_num in range(start, end + 1):
        # Skip if already processed
        if rule_num in progress['completed'] or rule_num in progress['skipped']:
            print(f"§{rule_num:3d} - already processed")
            continue

        print(f"§{rule_num:3d} - processing...", end=' ', flush=True)

        status, message = process_rule_with_claude(rule_num, spec_prompt)

        if status == 'success':
            progress['completed'].append(rule_num)
            success += 1
            print("✓")
        elif status == 'skipped':
            progress['skipped'].append(rule_num)
            skipped += 1
            print(f"⊘ ({message})")
        else:
            progress['failed'].append(rule_num)
            failed += 1
            print(f"✗ ({message})")

        # Save progress after each rule
        save_progress(progress)

    print("\n" + "="*60)
    print("BATCH COMPLETE")
    print("="*60)
    print(f"Success: {success}")
    print(f"Skipped: {skipped}")
    print(f"Failed: {failed}")
    print(f"Total completed: {len(progress['completed'])}/966 actual rules")
    print(f"Total processed: {len(progress['completed']) + len(progress['skipped'])}/972 files")

def main():
    if len(sys.argv) < 3:
        print("Usage: python process_rules_batch.py START END")
        print("Example: python process_rules_batch.py 1 50")
        sys.exit(1)

    # Load spec
    if not MARKDOWN_SPEC_FILE.exists():
        print(f"ERROR: {MARKDOWN_SPEC_FILE} not found")
        sys.exit(1)

    spec_content = MARKDOWN_SPEC_FILE.read_text(encoding='utf-8')
    spec_prompt = get_cleanup_prompt(spec_content)

    start = int(sys.argv[1])
    end = int(sys.argv[2])

    process_batch(start, end, spec_prompt)

if __name__ == '__main__':
    main()
