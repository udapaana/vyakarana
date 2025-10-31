#!/usr/bin/env python3
"""
Review script for processed OCR pages
Analyzes quality, consistency, and issues
"""

import json
from pathlib import Path
from collections import defaultdict

def review_processed_pages(repo_path, start_page=1, end_page=50):
    """Review processed pages and generate summary report"""

    repo = Path(repo_path)
    output_dir = repo / "structured_pages"

    stats = {
        "total_pages": 0,
        "valid_pages": 0,
        "needs_review": 0,
        "avg_preservation": 0.0,
        "total_ocr_corrections": 0,
        "correction_types": defaultdict(int),
        "topics": defaultdict(int),
        "critical_issues": [],
        "pages_by_quality": {"excellent": [], "good": [], "needs_review": []}
    }

    preservation_scores = []

    for page_num in range(start_page, end_page + 1):
        page_name = f"page_{page_num:03d}"
        validation_file = output_dir / f"{page_name}_validation.json"
        md_file = output_dir / f"{page_name}.md"

        if not validation_file.exists():
            print(f"⚠️  Page {page_num}: Not processed yet")
            continue

        stats["total_pages"] += 1

        # Load validation data
        with open(validation_file) as f:
            data = json.load(f)

        validation = data["validation"]
        ocr_corrections = data.get("ocr_corrections", [])

        # Track metrics
        preservation = validation.get("content_preserved_percentage", 0)
        preservation_scores.append(preservation)

        if validation.get("is_valid", False):
            stats["valid_pages"] += 1
        else:
            stats["needs_review"] += 1
            stats["critical_issues"].append({
                "page": page_num,
                "preservation": preservation,
                "issues": len(validation.get("differences", []))
            })

        stats["total_ocr_corrections"] += len(ocr_corrections)

        # Categorize corrections
        for correction in ocr_corrections:
            corr_type = correction.get("type", "unknown")
            stats["correction_types"][corr_type] += 1

        # Quality categorization
        if preservation >= 99.5:
            stats["pages_by_quality"]["excellent"].append(page_num)
        elif preservation >= 95.0:
            stats["pages_by_quality"]["good"].append(page_num)
        else:
            stats["pages_by_quality"]["needs_review"].append(page_num)

        # Extract topics from markdown
        if md_file.exists():
            with open(md_file) as f:
                content = f.read()
                # Parse front matter for topics
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 2:
                        try:
                            import yaml
                            front_matter = yaml.safe_load(parts[1])
                            for topic in front_matter.get('topics', []):
                                stats["topics"][topic] += 1
                        except:
                            pass

    # Calculate averages
    if preservation_scores:
        stats["avg_preservation"] = sum(preservation_scores) / len(preservation_scores)

    return stats

def print_report(stats, start_page, end_page):
    """Print formatted review report"""

    print(f"\n{'='*60}")
    print(f"  REVIEW REPORT: Pages {start_page}-{end_page}")
    print(f"{'='*60}\n")

    print(f"📊 Overall Statistics:")
    print(f"   Pages Processed:      {stats['total_pages']}/{end_page - start_page + 1}")
    print(f"   Valid Pages:          {stats['valid_pages']}")
    print(f"   Needs Review:         {stats['needs_review']}")
    print(f"   Avg Preservation:     {stats['avg_preservation']:.2f}%")
    print(f"   Total OCR Fixes:      {stats['total_ocr_corrections']}")
    print()

    print(f"✨ Quality Distribution:")
    print(f"   Excellent (≥99.5%):   {len(stats['pages_by_quality']['excellent'])} pages")
    print(f"   Good (≥95%):          {len(stats['pages_by_quality']['good'])} pages")
    print(f"   Needs Review (<95%):  {len(stats['pages_by_quality']['needs_review'])} pages")
    print()

    if stats['pages_by_quality']['needs_review']:
        print(f"⚠️  Pages needing review: {stats['pages_by_quality']['needs_review']}")
        print()

    print(f"🔧 OCR Correction Types:")
    for corr_type, count in sorted(stats['correction_types'].items(), key=lambda x: -x[1]):
        print(f"   {corr_type:20s}: {count:4d}")
    print()

    print(f"📚 Top Topics (by frequency):")
    top_topics = sorted(stats['topics'].items(), key=lambda x: -x[1])[:15]
    for topic, count in top_topics:
        print(f"   {topic:20s}: {count:4d} pages")
    print()

    if stats['critical_issues']:
        print(f"❌ Critical Issues ({len(stats['critical_issues'])}):")
        for issue in stats['critical_issues'][:5]:  # Show first 5
            print(f"   Page {issue['page']:3d}: {issue['preservation']:.1f}% preserved, "
                  f"{issue['issues']} issues")
        print()

    print(f"{'='*60}\n")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Review processed OCR pages')
    parser.add_argument('--start', type=int, default=1, help='Start page')
    parser.add_argument('--end', type=int, default=50, help='End page')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    stats = review_processed_pages('/Users/skmnktl/Downloads/ocr', args.start, args.end)

    if args.json:
        print(json.dumps(stats, indent=2, default=list))
    else:
        print_report(stats, args.start, args.end)
