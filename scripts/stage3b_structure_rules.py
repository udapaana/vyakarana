#!/usr/bin/env python3
"""
Stage 3B: Transform raw rules to structured format with full schema
Processes rules 1-50 from raw/ to structured/
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Base paths
BASE_DIR = Path("/Users/skmnktl/Downloads/ocr")
RAW_DIR = BASE_DIR / "phase3_rules/core/raw"
STRUCTURED_DIR = BASE_DIR / "phase3_rules/core/structured"

# Ensure output directory exists
STRUCTURED_DIR.mkdir(parents=True, exist_ok=True)


def extract_title(content: str, rule_num: int) -> str:
    """Extract title from the first substantial sentence after § N"""
    # Remove the frontmatter
    parts = content.split("---", 2)
    if len(parts) < 3:
        return f"Rule {rule_num}"

    body = parts[2].strip()

    # Remove § N prefix
    body = re.sub(r"^§\s*\d+\.\s*", "", body, flags=re.MULTILINE)

    # Get first sentence or first substantial line
    lines = [l.strip() for l in body.split("\n") if l.strip() and not l.startswith("#")]
    if not lines:
        return f"Rule {rule_num}"

    first_line = lines[0]

    # Extract up to first period, semicolon, or get first 100 chars
    match = re.match(r"^([^.;]{10,100})[.;]", first_line)
    if match:
        title = match.group(1).strip()
    else:
        # Take first clause or first 80 chars
        title = first_line[:80].strip()

    # Clean up title
    title = re.sub(r"\s+", " ", title)
    title = re.sub(r"\*+$", "", title)  # Remove trailing asterisks

    # Capitalize first letter if not already
    if title and not title[0].isupper():
        title = title[0].upper() + title[1:]

    return title


def classify_chapter_section(rule_num: int) -> Tuple[str, str]:
    """Classify chapter and section based on rule number"""
    if 1 <= rule_num <= 17:
        return "The Alphabet", "alphabet"
    elif 18 <= rule_num <= 50:
        return "Rules of Sandhi", "sandhi"
    else:
        return "Unknown", "unknown"


def extract_topics(content: str, rule_num: int, chapter: str) -> List[str]:
    """Extract topic keywords from content"""
    topics = []

    # Base topics from chapter
    if chapter == "The Alphabet":
        topics.append("alphabet")
    elif chapter == "Rules of Sandhi":
        topics.append("sandhi")

    content_lower = content.lower()

    # Common Sanskrit grammar topics
    topic_keywords = {
        "vowel": "vowels",
        "consonant": "consonants",
        "guttural": "gutturals",
        "palatal": "palatals",
        "lingual": "linguals",
        "dental": "dentals",
        "labial": "labials",
        "nasal": "nasals",
        "semivowel": "semivowels",
        "sibilant": "sibilants",
        "aspirat": "aspiration",
        "anusvāra": "anusvara",
        "anusv?ra": "anusvara",
        "visarga": "visarga",
        "sandhi": "sandhi",
        "combination": "combination",
        "substitution": "substitution",
        "elision": "elision",
        "euphonic": "euphonic",
        "hiatus": "hiatus",
        "diphthong": "diphthongs",
        "pragṛhya": "pragrihya",
        "pragr?hya": "pragrihya",
        "doubling": "doubling",
        "duplication": "doubling",
        "assimilation": "assimilation",
        "dissimilar": "dissimilar-vowels",
        "similar": "similar-vowels",
        "long": "long-vowels",
        "short": "short-vowels",
        "guna": "guna",
        "vṛddhi": "vrddhi",
        "vrddhi": "vrddhi",
        "pada": "pada",
        "avagraha": "avagraha",
    }

    for keyword, topic in topic_keywords.items():
        if re.search(keyword, content_lower):
            if topic not in topics:
                topics.append(topic)

    # Limit to 5 most relevant
    return topics[:5] if len(topics) <= 5 else topics[:5]


def extract_devanagari_terms(content: str) -> List[str]:
    """Extract Devanagari terms for word index"""
    # Find all Devanagari text
    devanagari_pattern = r"[\u0900-\u097F]+"
    matches = re.findall(devanagari_pattern, content)

    # Deduplicate and filter
    unique_terms = []
    seen = set()

    for match in matches:
        # Clean the term
        term = match.strip()
        # Skip very long strings (likely sentences)
        if len(term) > 15:
            continue
        # Skip if already seen
        if term in seen:
            continue
        seen.add(term)
        unique_terms.append(term)

    # Limit to 15 most important terms
    return unique_terms[:15]


def extract_panini_refs(content: str) -> List[str]:
    """Extract Pāṇini references from footnotes"""
    refs = []

    # Patterns for Pāṇini references
    patterns = [
        r"Pāṇ\.\s+([IVX]+)\.\s*(\d+)\.\s*(\d+)",
        r"Páṇ\.\s+([IVX]+)\.\s*(\d+)\.\s*(\d+)",
        r"Pan\.\s+([IVX]+)\.\s*(\d+)\.\s*(\d+)",
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            book = match.group(1)
            chapter = match.group(2)
            sutra = match.group(3)
            ref = f"{book}.{chapter}.{sutra}"
            if ref not in refs:
                refs.append(ref)

    return sorted(set(refs))


def extract_cross_refs(content: str, rule_num: int) -> List[str]:
    """Extract cross-references to other rules"""
    refs = []

    # Patterns for § N references
    patterns = [
        r"§\s*(\d+)",
        r"see\s+(\d+)",
        r"art\.\s+(\d+)",
        r"rule\s+(\d+)",
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            ref_num = match.group(1)
            ref = f"§ {ref_num}"
            # Don't include self-reference
            if int(ref_num) != rule_num and ref not in refs:
                refs.append(ref)

    return sorted(refs, key=lambda x: int(x.split()[1]))


def format_structured_rule(raw_content: str, rule_num: int) -> str:
    """Transform raw rule content to structured format"""

    # Parse the raw YAML frontmatter
    parts = raw_content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"Invalid format for rule {rule_num}")

    raw_yaml = parts[1].strip()
    body = parts[2].strip()

    # Extract metadata
    title = extract_title(raw_content, rule_num)
    chapter, section = classify_chapter_section(rule_num)
    topics = extract_topics(body, rule_num, chapter)
    word_index = extract_devanagari_terms(body)
    panini_refs = extract_panini_refs(body)
    cross_refs = extract_cross_refs(body, rule_num)

    # Extract page info from raw YAML
    page_start_match = re.search(r'page_start:\s*["\']?(\w+)["\']?', raw_yaml)
    page_end_match = re.search(r'page_end:\s*["\']?(\w+)["\']?', raw_yaml)
    source_pages_match = re.search(r"source_pages:\s*\[(.*?)\]", raw_yaml, re.DOTALL)

    page_start = page_start_match.group(1) if page_start_match else str(rule_num)
    page_end = page_end_match.group(1) if page_end_match else str(rule_num)

    if source_pages_match:
        source_pages_str = source_pages_match.group(1)
        source_pages = [p.strip(" \"'") for p in source_pages_str.split(",")]
    else:
        source_pages = [f"{rule_num:03d}"]

    # Build structured YAML frontmatter
    yaml_lines = [
        "---",
        f"rule_number: {rule_num}",
        f'rule_id: "§ {rule_num}"',
        f'title: "{title}"',
        f'chapter: "{chapter}"',
        f'section: "{section}"',
    ]

    # Handle page_start/page_end (quote if contains letters)
    if page_start.isdigit():
        yaml_lines.append(f"page_start: {page_start}")
    else:
        yaml_lines.append(f'page_start: "{page_start}"')

    if page_end.isdigit():
        yaml_lines.append(f"page_end: {page_end}")
    else:
        yaml_lines.append(f'page_end: "{page_end}"')

    # Add topics
    yaml_lines.append("topics:")
    for topic in topics:
        yaml_lines.append(f"  - {topic}")

    # Add word_index
    yaml_lines.append("word_index:")
    if word_index:
        for term in word_index:
            yaml_lines.append(f"  - {term}")
    else:
        yaml_lines.append("  []")

    # Add panini_refs
    yaml_lines.append("panini_refs:")
    if panini_refs:
        for ref in panini_refs:
            yaml_lines.append(f'  - "{ref}"')
    else:
        yaml_lines.append("  []")

    # Add cross_refs
    yaml_lines.append("cross_refs:")
    if cross_refs:
        for ref in cross_refs:
            yaml_lines.append(f'  - "{ref}"')
    else:
        yaml_lines.append("  []")

    # Add source_pages
    yaml_lines.append("source_pages:")
    for page in source_pages:
        yaml_lines.append(f'  - "{page}"')

    yaml_lines.append('extraction_status: "structured"')
    yaml_lines.append("---")

    # Build content section with title heading
    content_lines = ["", f"## {title}", ""]

    # Add the body content (removing the § N prefix if present)
    body_clean = re.sub(r"^§\s*\d+\.\s*", "", body, flags=re.MULTILINE)
    content_lines.append(body_clean)

    # Combine everything
    return "\n".join(yaml_lines + content_lines)


def process_rule(rule_num: int) -> Dict:
    """Process a single rule from raw to structured"""
    raw_file = RAW_DIR / f"rule_{rule_num:03d}.md"
    structured_file = STRUCTURED_DIR / f"rule_{rule_num:03d}.md"

    result = {"rule_num": rule_num, "success": False, "title": None, "error": None}

    try:
        # Read raw content
        if not raw_file.exists():
            result["error"] = f"Raw file not found: {raw_file}"
            return result

        raw_content = raw_file.read_text(encoding="utf-8")

        # Transform to structured format
        structured_content = format_structured_rule(raw_content, rule_num)

        # Extract title for reporting
        title_match = re.search(r'^title: "(.+)"$', structured_content, re.MULTILINE)
        if title_match:
            result["title"] = title_match.group(1)

        # Write structured content
        structured_file.write_text(structured_content, encoding="utf-8")

        result["success"] = True

    except Exception as e:
        result["error"] = str(e)

    return result


def main():
    """Process all rules 1-50"""
    print("Stage 3B: Structuring Rules 1-50")
    print("=" * 60)

    results = []
    successful = 0
    failed = 0

    for rule_num in range(1, 51):
        print(f"Processing rule {rule_num:03d}...", end=" ")
        result = process_rule(rule_num)
        results.append(result)

        if result["success"]:
            print(f"✓ {result['title']}")
            successful += 1
        else:
            print(f"✗ Error: {result['error']}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"SUMMARY:")
    print(f"  Total processed: {len(results)}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")

    # Show sample of titles
    print(f"\nSample of generated titles:")
    sample_titles = [r for r in results if r["success"] and r["title"]][:10]
    for result in sample_titles:
        print(f"  § {result['rule_num']:3d}: {result['title']}")

    if failed > 0:
        print(f"\nFailed rules:")
        for result in results:
            if not result["success"]:
                print(f"  § {result['rule_num']:3d}: {result['error']}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit(main())
