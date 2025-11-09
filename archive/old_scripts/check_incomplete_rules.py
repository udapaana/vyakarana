#!/usr/bin/env python3
"""
Check for rules that might be incomplete due to page continuations
"""

import re
from pathlib import Path
import yaml


def extract_yaml(content: str) -> dict:
    """Extract YAML frontmatter"""
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        return yaml.safe_load(parts[1])
    except:
        return {}


def main():
    structured_dir = Path("phase2_structured")
    rules_dir = Path("phase3_rules")

    # Find all pages with continuation markers and their rules
    pages_with_continuations = {}

    for page_file in sorted(structured_dir.glob("page_*.md")):
        with open(page_file) as f:
            content = f.read()

        yaml_data = extract_yaml(content)

        if "continues_to" in yaml_data:
            rule = yaml_data.get("rule", "")
            page_num = yaml_data.get("page", "")
            continues_to = yaml_data.get("continues_to", "")

            # Extract rule numbers
            rule_nums = []
            if isinstance(rule, str):
                # Look for § N or § N-M patterns
                matches = re.findall(r"§\s*(\d+)(?:\s*[-–]\s*(\d+))?", rule)
                for match in matches:
                    if match[1]:  # Range
                        rule_nums.extend(range(int(match[0]), int(match[1]) + 1))
                    else:
                        rule_nums.append(int(match[0]))

            for rule_num in rule_nums:
                if rule_num not in pages_with_continuations:
                    pages_with_continuations[rule_num] = []
                pages_with_continuations[rule_num].append(
                    {
                        "page": page_num,
                        "continues_to": continues_to,
                        "page_file": page_file.name,
                    }
                )

    print("=" * 80)
    print("CHECKING FOR INCOMPLETE MULTI-PAGE RULES")
    print("=" * 80)
    print(f"\nFound {len(pages_with_continuations)} rules with page continuations")
    print()

    # Check extracted rules
    incomplete_rules = []

    for rule_num in sorted(pages_with_continuations.keys()):
        rule_file = rules_dir / f"rule_{rule_num:03d}.md"

        if not rule_file.exists():
            print(f"⚠️  Rule {rule_num:03d}: Not extracted yet")
            continue

        with open(rule_file) as f:
            content = f.read()

        yaml_data = extract_yaml(content)

        # Get metadata
        page_start = yaml_data.get("page_start", "")
        page_end = yaml_data.get("page_end", "")
        source_pages = yaml_data.get("source_pages", [])

        # Get expected continuation info
        continuation_info = pages_with_continuations[rule_num]

        # Check if this is potentially incomplete
        is_incomplete = False
        reasons = []

        # Check 1: page_start == page_end but continues_to exists
        if page_start == page_end and continuation_info:
            is_incomplete = True
            reasons.append(f"page_start == page_end ({page_start}) but rule continues")

        # Check 2: source_pages only has one page but continues_to exists
        if len(source_pages) == 1 and continuation_info:
            is_incomplete = True
            reasons.append(
                f"only 1 source page but rule continues to {continuation_info[0]['continues_to']}"
            )

        # Check 3: Check for incomplete sentences (ends with "is", "are", "the", etc.)
        content_end = content.strip()[-200:]
        incomplete_patterns = [
            r"\bis\s*\[?\^?\d*\]?\s*$",  # ends with "is"
            r"\bare\s*\[?\^?\d*\]?\s*$",  # ends with "are"
            r"\bthe\s*\[?\^?\d*\]?\s*$",  # ends with "the"
            r"\band\s*\[?\^?\d*\]?\s*$",  # ends with "and"
            r"\bor\s*\[?\^?\d*\]?\s*$",  # ends with "or"
            r"\bof\s*\[?\^?\d*\]?\s*$",  # ends with "of"
            r"\bto\s*\[?\^?\d*\]?\s*$",  # ends with "to"
        ]

        for pattern in incomplete_patterns:
            if re.search(pattern, content_end, re.IGNORECASE):
                is_incomplete = True
                match = re.search(pattern, content_end, re.IGNORECASE)
                reasons.append(f"ends with '{match.group().strip()}'")
                break

        if is_incomplete:
            incomplete_rules.append(
                {
                    "rule_num": rule_num,
                    "page_start": page_start,
                    "page_end": page_end,
                    "source_pages": source_pages,
                    "continuation_info": continuation_info,
                    "reasons": reasons,
                }
            )

            print(f"\n❌ Rule {rule_num:03d} - POTENTIALLY INCOMPLETE")
            print(f"   Current: page {page_start} → {page_end}")
            print(f"   Source pages: {source_pages}")
            print(f"   Expected continuation: {continuation_info[0]['continues_to']}")
            for reason in reasons:
                print(f"   ⚠️  {reason}")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total rules with continuations: {len(pages_with_continuations)}")
    print(f"Potentially incomplete: {len(incomplete_rules)}")

    if incomplete_rules:
        print("\nRules to fix:")
        for rule in incomplete_rules:
            print(f"  § {rule['rule_num']:03d}")

    return incomplete_rules


if __name__ == "__main__":
    incomplete = main()
