#!/usr/bin/env python3
"""
Process only the missing rules (not yet in rules_cleaned/)
With proper rate limiting to avoid API limits.
"""

import json
from pathlib import Path
import sys
import os
import time

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

def get_missing_rules():
    """Get list of rules that haven't been cleaned yet"""
    all_rules = set(range(1, 973))
    cleaned = set()

    if OUTPUT_DIR.exists():
        for f in OUTPUT_DIR.glob('*.md'):
            rule_num = int(f.stem)
            cleaned.add(rule_num)

    return sorted(all_rules - cleaned)

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

def process_missing(delay=2.0, max_rules=None):
    """Process missing rules with rate limiting"""
    # Load spec
    if not MARKDOWN_SPEC_FILE.exists():
        print(f"ERROR: {MARKDOWN_SPEC_FILE} not found")
        return

    spec_content = MARKDOWN_SPEC_FILE.read_text(encoding='utf-8')
    spec_prompt = get_cleanup_prompt(spec_content)

    # Get missing rules
    missing = get_missing_rules()

    if max_rules:
        missing = missing[:max_rules]

    print("="*60)
    print(f"Processing {len(missing)} missing rules")
    print(f"Delay between calls: {delay}s")
    print("="*60 + "\n")

    progress = load_progress()
    success = 0
    failed = 0
    skipped = 0

    for i, rule_num in enumerate(missing, 1):
        print(f"[{i}/{len(missing)}] §{rule_num:3d} - processing...", end=' ', flush=True)

        status, message = process_rule_with_claude(rule_num, spec_prompt)

        if status == 'success':
            if rule_num not in progress['completed']:
                progress['completed'].append(rule_num)
            # Remove from failed if it was there
            if rule_num in progress['failed']:
                progress['failed'].remove(rule_num)
            success += 1
            print("✓")
        elif status == 'skipped':
            if rule_num not in progress['skipped']:
                progress['skipped'].append(rule_num)
            skipped += 1
            print(f"⊘ ({message})")
        else:
            if rule_num not in progress['failed']:
                progress['failed'].append(rule_num)
            failed += 1
            print(f"✗ ({message})")

        # Save progress after each rule
        save_progress(progress)

        # Rate limiting
        if i < len(missing):
            time.sleep(delay)

    print("\n" + "="*60)
    print("PROCESSING COMPLETE")
    print("="*60)
    print(f"Success: {success}")
    print(f"Skipped: {skipped}")
    print(f"Failed: {failed}")
    print(f"\nTotal progress:")
    print(f"  Completed: {len(progress['completed'])}/966 actual rules")
    print(f"  Skipped: {len(progress['skipped'])}/6 placeholders")
    print(f"  Failed: {len(progress['failed'])} rules")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Process missing cleaned rules')
    parser.add_argument('--delay', type=float, default=2.0,
                       help='Delay between API calls in seconds (default: 2.0)')
    parser.add_argument('--max', type=int, default=None,
                       help='Maximum number of rules to process (default: all)')

    args = parser.parse_args()

    process_missing(delay=args.delay, max_rules=args.max)
