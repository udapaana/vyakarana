#!/usr/bin/env python3
"""Comprehensive quality validation for all 972 rules"""
import re
from pathlib import Path
from collections import defaultdict

RULES_DIR = Path("phase4_rules")

issues = defaultdict(list)
stats = {
    "total": 0,
    "valid_yaml": 0,
    "has_content": 0,
    "has_sanskrit": 0,
    "has_image": 0,
    "complete": 0
}

def validate_rule(rule_num: int):
    """Validate a single rule file"""
    file = RULES_DIR / f"rule_{rule_num:03d}.md"
    
    if not file.exists():
        issues["missing_file"].append(rule_num)
        return
    
    stats["total"] += 1
    content = file.read_text()
    
    # Check YAML frontmatter
    if not content.startswith('---\n'):
        issues["invalid_yaml"].append(rule_num)
        return
    
    stats["valid_yaml"] += 1
    
    # Check for required YAML fields
    required_fields = ['rule:', 'page:', 'chapter:', 'image:']
    for field in required_fields:
        if field not in content:
            issues[f"missing_{field[:-1]}"].append(rule_num)
    
    # Check content length
    if len(content) > 500:
        stats["has_content"] += 1
    else:
        if 'MISSING FROM OCR' not in content:
            issues["minimal_content"].append(rule_num)
    
    # Check for Sanskrit tags
    if '@deva[' in content:
        stats["has_sanskrit"] += 1
        
        # Validate Sanskrit tag format
        invalid_tags = re.findall(r'@deva\[[^\]]*\](?!\s*@\[)', content)
        if '@[' not in content and invalid_tags:
            # Some tags, but no IAST (acceptable for §39-972)
            pass
    
    # Check image path format
    img_match = re.search(r'image:\s*/images/(\d{3})\.png', content)
    if img_match:
        stats["has_image"] += 1
    else:
        issues["invalid_image_path"].append(rule_num)
    
    # Check for old schema artifacts
    if 'rule_number:' in content:
        issues["old_schema_artifact"].append(rule_num)
    
    # Check for OCR artifacts
    if '[Internal page:' in content:
        issues["internal_page_marker"].append(rule_num)
    
    # Mark as complete if all checks pass
    if (len(content) > 500 and 
        '@deva[' in content and
        img_match and
        'MISSING FROM OCR' not in content):
        stats["complete"] += 1

print("=" * 70)
print("QUALITY VALIDATION - ALL 972 RULES")
print("=" * 70)

for num in range(1, 973):
    validate_rule(num)

print("\nSTATISTICS:")
print("-" * 70)
print(f"Total rules validated:    {stats['total']}")
print(f"Valid YAML frontmatter:   {stats['valid_yaml']}")
print(f"Has substantial content:  {stats['has_content']} ({stats['has_content']/stats['total']*100:.1f}%)")
print(f"Has Sanskrit tags:        {stats['has_sanskrit']} ({stats['has_sanskrit']/stats['total']*100:.1f}%)")
print(f"Has valid image path:     {stats['has_image']} ({stats['has_image']/stats['total']*100:.1f}%)")
print(f"✓ COMPLETE:               {stats['complete']} ({stats['complete']/stats['total']*100:.1f}%)")

print("\n" + "=" * 70)
print("ISSUES FOUND:")
print("=" * 70)

if not any(issues.values()):
    print("✓ No issues found!")
else:
    for issue_type, rule_nums in sorted(issues.items()):
        if rule_nums:
            print(f"\n{issue_type}: {len(rule_nums)} rules")
            print(f"  {rule_nums[:10]}" + ("..." if len(rule_nums) > 10 else ""))

print("\n" + "=" * 70)
