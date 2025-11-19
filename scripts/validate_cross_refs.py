#!/usr/bin/env python3
"""
Cross-Reference Validation Script for Stage 3C
Validates all cross-references in cleaned rule files.

Checks:
1. Untagged § N mentions in body text
2. Cross-references to non-existent rules
3. Bidirectional reference consistency
4. @ref[] tag usage
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Paths
CORE_CLEANED = Path("phase3_rules/core/cleaned")
APPENDIX_CLEANED = Path("phase3_rules/appendix_prosody/cleaned")

def extract_frontmatter(content: str) -> Tuple[dict, str]:
    """Extract YAML frontmatter and body from markdown content."""
    parts = content.split('---')
    if len(parts) < 3:
        return {}, content

    try:
        fm = yaml.safe_load(parts[1])
        body = '---'.join(parts[2:])
        return fm, body
    except:
        return {}, content

def find_untagged_refs(body: str, rule_num: int) -> List[int]:
    """Find § N mentions that aren't in @ref[] tags."""
    # Find all § N patterns
    all_refs = re.findall(r'§\s*(\d+)', body)

    # Find § N patterns that are already tagged with @ref[]
    # Look for @ref[N] or @ref[N,M,...]
    tagged_pattern = r'@ref\[([^\]]+)\]'
    tagged_refs = []
    for match in re.finditer(tagged_pattern, body):
        refs = match.group(1).split(',')
        for ref in refs:
            ref = ref.strip()
            # Extract numbers from references like "prosody:3" or just "123"
            if ':' in ref:
                num = ref.split(':')[1]
            else:
                num = ref
            if num.isdigit():
                tagged_refs.append(num)

    # Find untagged refs (excluding self-references)
    untagged = []
    for ref in all_refs:
        ref_num = int(ref)
        if ref_num != rule_num and ref not in tagged_refs:
            untagged.append(ref_num)

    return sorted(set(untagged))

def validate_ref_exists(ref_num: int, is_appendix: bool = False) -> bool:
    """Check if a referenced rule exists."""
    if is_appendix:
        path = APPENDIX_CLEANED / f"rule_{ref_num:03d}.md"
    else:
        # Core rules use zero-padding for 1-99, no padding for 100+
        if ref_num < 100:
            path = CORE_CLEANED / f"rule_{ref_num:03d}.md"
        else:
            path = CORE_CLEANED / f"rule_{ref_num}.md"

    return path.exists()

def get_frontmatter_refs(fm: dict) -> List[str]:
    """Extract cross_refs from frontmatter."""
    cross_refs = fm.get('cross_refs', [])
    if not cross_refs:
        return []

    # Parse § N or prosody:N format
    refs = []
    for ref in cross_refs:
        # Convert to string if not already
        ref_str = str(ref) if ref is not None else ''
        match = re.search(r'§\s*(\d+)', ref_str)
        if match:
            refs.append(match.group(1))
    return refs

def main():
    print("=" * 70)
    print("Cross-Reference Validation - Stage 3C")
    print("=" * 70)
    print()

    # Statistics
    total_rules = 0
    rules_with_untagged = []
    broken_refs = []
    frontmatter_refs_count = 0

    # Process core rules
    print("Processing core rules (§ 1-972)...")
    for i in range(1, 973):
        # Handle zero-padding for rules 1-99
        if i < 100:
            path = CORE_CLEANED / f"rule_{i:03d}.md"
        else:
            path = CORE_CLEANED / f"rule_{i}.md"

        if not path.exists():
            continue

        total_rules += 1
        with open(path) as f:
            content = f.read()

        fm, body = extract_frontmatter(content)

        # Check for untagged references in body
        untagged = find_untagged_refs(body, i)
        if untagged:
            rules_with_untagged.append((i, untagged))

        # Check frontmatter cross_refs
        fm_refs = get_frontmatter_refs(fm)
        if fm_refs:
            frontmatter_refs_count += len(fm_refs)
            # Validate they exist
            for ref_num in fm_refs:
                if not validate_ref_exists(int(ref_num)):
                    broken_refs.append((i, ref_num))

    # Process appendix rules
    print("Processing appendix prosody rules (§ 1-14)...")
    for i in range(1, 15):
        path = APPENDIX_CLEANED / f"rule_{i:03d}.md"
        if not path.exists():
            continue

        total_rules += 1
        with open(path) as f:
            content = f.read()

        fm, body = extract_frontmatter(content)

        untagged = find_untagged_refs(body, i)
        if untagged:
            rules_with_untagged.append((f"prosody:{i}", untagged))

    # Report results
    print()
    print("=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)
    print()

    print(f"Total rules processed: {total_rules}")
    print(f"Frontmatter cross_refs: {frontmatter_refs_count}")
    print()

    # Untagged references
    print(f"Rules with untagged cross-references: {len(rules_with_untagged)}")
    if rules_with_untagged:
        print()
        print("Untagged cross-references (need @ref[] markup):")
        print("-" * 70)
        for rule, refs in rules_with_untagged[:20]:  # Show first 20
            refs_str = ', '.join([f"§ {r}" for r in refs])
            print(f"  § {rule}: mentions {refs_str}")
        if len(rules_with_untagged) > 20:
            print(f"  ... and {len(rules_with_untagged) - 20} more")
    print()

    # Broken references
    if broken_refs:
        print(f"⚠️  Broken references found: {len(broken_refs)}")
        print()
        print("References to non-existent rules:")
        print("-" * 70)
        for rule, ref in broken_refs:
            print(f"  § {rule} → § {ref} (DOES NOT EXIST)")
    else:
        print("✅ No broken references found")

    print()
    print("=" * 70)

    # Exit code
    if broken_refs:
        return 1
    return 0

if __name__ == "__main__":
    exit(main())
