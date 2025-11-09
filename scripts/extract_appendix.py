#!/usr/bin/env python3
"""Extract appendix content from OCR files for Phase 4"""

from pathlib import Path
import re

# Directories
OCR_DIR = Path("phase1_ocr/sources/official_1931")
APPENDIX_DIR = Path("phase4_appendix")
APPENDIX_DIR.mkdir(exist_ok=True)

# Appendix pages: external 549-732, internal 535-732
APPENDIX_START_EXTERNAL = 549
APPENDIX_END_EXTERNAL = 732

def extract_internal_page(ocr_file: Path) -> int:
    """Extract internal page number from OCR file"""
    try:
        content = ocr_file.read_text(encoding='utf-8', errors='ignore')
        match = re.search(r'\[Internal page:\s*(\d+)\]', content)
        if match:
            return int(match.group(1))
    except:
        pass
    return None

def clean_ocr_content(content: str) -> str:
    """Clean OCR content for appendix"""
    # Remove internal page markers
    content = re.sub(r'\[Internal page:\s*\d+\]\s*\n?', '', content)

    # Remove page header patterns like "§ 8-13 ]                PROSODY.                                3"
    content = re.sub(r'^§?\s*[\d–-]+\s*\].*?(?:PROSODY|SANSKRIT GRAMMAR).*?\d+\s*$', '', content, flags=re.MULTILINE)

    # Clean up excessive whitespace
    content = re.sub(r'\n{3,}', '\n\n', content)

    return content.strip()

def extract_appendix_content():
    """Extract all appendix content"""

    all_content = []
    page_mapping = []

    print("=" * 70)
    print("EXTRACTING APPENDIX CONTENT")
    print("=" * 70)

    for ext_page in range(APPENDIX_START_EXTERNAL, APPENDIX_END_EXTERNAL + 1):
        ocr_file = OCR_DIR / f"{ext_page:03d}.txt"

        if not ocr_file.exists():
            print(f"⚠ Missing: {ext_page:03d}.txt")
            continue

        # Extract internal page number
        int_page = extract_internal_page(ocr_file)

        # Read and clean content
        content = ocr_file.read_text(encoding='utf-8', errors='ignore')
        cleaned = clean_ocr_content(content)

        if cleaned:
            all_content.append(cleaned)
            page_mapping.append(f"External {ext_page:03d} → Internal {int_page:03d}")

            if ext_page % 10 == 0:
                print(f"Processed: {ext_page}/{APPENDIX_END_EXTERNAL}")

    print(f"\n✓ Extracted {len(all_content)} pages of content")

    return "\n\n---\n\n".join(all_content), page_mapping

def create_appendix_sections():
    """Create organized appendix sections"""

    # Extract all content
    full_content, page_mapping = extract_appendix_content()

    # Create main appendix content file
    appendix_content = f"""---
title: "Appendix: Prosody (Complete Content)"
section: appendix
pages: 535-732
source_pages:
  official_1931: [549-732]
topics: [prosody, versification, metres, Sanskrit-poetry]
extraction_date: 2025-11-09
---

# Appendix: Prosody

**Complete extracted content from Kale's Higher Sanskrit Grammar**

## About This Appendix

This appendix covers the laws of Sanskrit versification and metrical composition (Prosody).

### Coverage
- Internal pages: 535-732
- External pages: 549-732
- Total pages: 183

### Topics Covered
- Fundamental rules of Sanskrit verse
- Syllable measurement (mātrā)
- Light and heavy syllables (laghu, guru)
- Gaṇas (syllabic feet)
- Samavṛttas (regular metres)
- Ardhasamavṛttas (semi-regular metres)
- Viṣama (irregular metres)
- Jātis (mātrā-based metres)
- Common metres with examples

---

## Full Content

{full_content}

---

## Page Mapping

{chr(10).join(page_mapping)}
"""

    output_file = APPENDIX_DIR / "prosody_complete.md"
    output_file.write_text(appendix_content, encoding='utf-8')

    print("\n" + "=" * 70)
    print("APPENDIX EXTRACTION COMPLETE")
    print("=" * 70)
    print(f"Created: {output_file}")
    print(f"Pages extracted: {len(page_mapping)}")
    print(f"Total content size: {len(full_content):,} characters")
    print("=" * 70)

if __name__ == "__main__":
    create_appendix_sections()
