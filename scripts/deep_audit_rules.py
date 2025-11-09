#!/usr/bin/env python3
"""Deep audit of all rules to get real quality metrics"""

from pathlib import Path
import re

PHASE3_DIR = Path("phase3_rules")

def audit_rule(file_path: Path) -> dict:
    """Audit a single rule file for quality metrics"""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except:
        return {
            'exists': False,
            'readable': False
        }

    rule_num = file_path.stem.replace('rule_', '')

    # Check YAML frontmatter
    has_yaml = content.startswith('---')

    # Extract content after frontmatter
    parts = content.split('---', 2)
    if len(parts) >= 3:
        frontmatter = parts[1]
        body = parts[2]
    else:
        frontmatter = ""
        body = content

    # Quality indicators
    has_deva_tags = '@deva[' in body
    has_iast_tags = '@[' in body and '@deva[' not in body[:body.find('@[') if '@[' in body else 0]

    # Problem indicators
    has_auto_extracted = 'AUTO-EXTRACTED' in content
    has_manual_refine = 'To be manually refined' in content
    has_needs_review = 'needs review' in content.lower()
    has_todo = 'TODO' in content or 'FIXME' in content
    has_stub = 'stub' in content.lower()
    has_incomplete = 'incomplete' in content.lower()

    # Content quality
    body_lines = [line for line in body.split('\n') if line.strip() and not line.strip().startswith('<!--')]
    content_lines = len(body_lines)
    content_chars = len(body.strip())

    # Check for chapter assignment
    has_chapter = 'chapter:' in frontmatter and 'TBD' not in frontmatter

    # Check for examples
    has_examples = bool(re.search(r'e\.g\.|Ex\.|example|Example', body))

    # Check footnotes
    has_footnotes = '[^' in body or 'footnotes:' in frontmatter

    # Empty or minimal content
    is_minimal = content_chars < 100
    is_stub = content_lines < 3 or is_minimal

    return {
        'exists': True,
        'readable': True,
        'rule_num': rule_num,
        'has_yaml': has_yaml,
        'has_deva_tags': has_deva_tags,
        'has_iast_tags': has_iast_tags,
        'has_auto_extracted': has_auto_extracted,
        'has_manual_refine': has_manual_refine,
        'has_needs_review': has_needs_review,
        'has_todo': has_todo,
        'has_stub_marker': has_stub,
        'has_incomplete': has_incomplete,
        'has_chapter': has_chapter,
        'has_examples': has_examples,
        'has_footnotes': has_footnotes,
        'content_lines': content_lines,
        'content_chars': content_chars,
        'is_stub': is_stub,
        'is_minimal': is_minimal
    }

def main():
    print("=" * 80)
    print("DEEP AUDIT OF ALL 972 RULES")
    print("=" * 80)

    all_results = []

    for i in range(1, 973):
        file_path = PHASE3_DIR / f"rule_{i:03d}.md"
        result = audit_rule(file_path)
        all_results.append(result)

    # Calculate statistics
    total = len(all_results)
    exists = sum(1 for r in all_results if r.get('exists', False))
    readable = sum(1 for r in all_results if r.get('readable', False))

    has_yaml = sum(1 for r in all_results if r.get('has_yaml', False))
    has_deva = sum(1 for r in all_results if r.get('has_deva_tags', False))
    has_iast = sum(1 for r in all_results if r.get('has_iast_tags', False))

    auto_extracted = sum(1 for r in all_results if r.get('has_auto_extracted', False))
    manual_refine = sum(1 for r in all_results if r.get('has_manual_refine', False))
    needs_review = sum(1 for r in all_results if r.get('has_needs_review', False))
    has_todo = sum(1 for r in all_results if r.get('has_todo', False))

    has_chapter = sum(1 for r in all_results if r.get('has_chapter', False))
    has_examples = sum(1 for r in all_results if r.get('has_examples', False))
    has_footnotes = sum(1 for r in all_results if r.get('has_footnotes', False))

    is_stub = sum(1 for r in all_results if r.get('is_stub', False))
    is_minimal = sum(1 for r in all_results if r.get('is_minimal', False))

    # Quality tiers
    high_quality = sum(1 for r in all_results
                       if r.get('has_yaml') and r.get('has_deva_tags')
                       and not r.get('has_auto_extracted')
                       and not r.get('is_stub')
                       and r.get('content_chars', 0) > 200)

    medium_quality = sum(1 for r in all_results
                         if r.get('has_yaml') and r.get('has_deva_tags')
                         and r.get('content_chars', 0) > 100
                         and not r.get('is_stub'))

    print(f"\n{'EXISTENCE METRICS':-^80}")
    print(f"Total rules expected:        {total}")
    print(f"Files exist:                 {exists} ({exists*100//total}%)")
    print(f"Files readable:              {readable} ({readable*100//total}%)")
    print(f"Missing files:               {total - exists}")

    print(f"\n{'FORMAT METRICS':-^80}")
    print(f"Has YAML frontmatter:        {has_yaml} ({has_yaml*100//total}%)")
    print(f"Has chapter assigned:        {has_chapter} ({has_chapter*100//total}%)")

    print(f"\n{'CONTENT QUALITY METRICS':-^80}")
    print(f"Has @deva[] tags:            {has_deva} ({has_deva*100//total}%)")
    print(f"Has @[] IAST tags:           {has_iast} ({has_iast*100//total}%)")
    print(f"Has examples:                {has_examples} ({has_examples*100//total}%)")
    print(f"Has footnotes:               {has_footnotes} ({has_footnotes*100//total}%)")

    print(f"\n{'PROBLEM INDICATORS':-^80}")
    print(f"Marked AUTO-EXTRACTED:       {auto_extracted}")
    print(f"Marked 'manual refine':      {manual_refine}")
    print(f"Marked 'needs review':       {needs_review}")
    print(f"Has TODO/FIXME:              {has_todo}")
    print(f"Is stub (< 3 lines):         {is_stub}")
    print(f"Is minimal (< 100 chars):    {is_minimal}")

    print(f"\n{'QUALITY TIERS':-^80}")
    print(f"HIGH quality:                {high_quality} ({high_quality*100//total}%)")
    print(f"  - Has YAML, Devanagari tags, >200 chars, no AUTO-EXTRACTED marker")
    print(f"MEDIUM quality:              {medium_quality} ({medium_quality*100//total}%)")
    print(f"  - Has YAML, Devanagari tags, >100 chars")
    print(f"LOW quality:                 {total - medium_quality} ({(total-medium_quality)*100//total}%)")

    # List problematic rules
    print(f"\n{'RULES NEEDING ATTENTION':-^80}")

    missing = [r['rule_num'] for r in all_results if not r.get('exists')]
    if missing:
        print(f"\nMissing files ({len(missing)}):")
        print(", ".join(f"§{n}" for n in missing[:20]))
        if len(missing) > 20:
            print(f"  ...and {len(missing) - 20} more")

    stubs = [r['rule_num'] for r in all_results if r.get('is_stub')]
    if stubs:
        print(f"\nStub files ({len(stubs)}):")
        print(", ".join(f"§{n}" for n in stubs[:20]))
        if len(stubs) > 20:
            print(f"  ...and {len(stubs) - 20} more")

    auto_ext = [r['rule_num'] for r in all_results if r.get('has_auto_extracted')]
    if auto_ext:
        print(f"\nAUTO-EXTRACTED markers ({len(auto_ext)}):")
        print(", ".join(f"§{n}" for n in auto_ext[:30]))
        if len(auto_ext) > 30:
            print(f"  ...and {len(auto_ext) - 30} more")

    no_chapter = [r['rule_num'] for r in all_results if r.get('exists') and not r.get('has_chapter')]
    if no_chapter:
        print(f"\nNo chapter assigned ({len(no_chapter)}):")
        print(", ".join(f"§{n}" for n in no_chapter[:30]))
        if len(no_chapter) > 30:
            print(f"  ...and {len(no_chapter) - 30} more")

    print("\n" + "=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
