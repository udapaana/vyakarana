# Document Structure Guide

## Overview

The aggregated markdown output follows a consistent hierarchical structure suitable for markdown parsers, static site generators, and document navigation tools.

## Heading Hierarchy

### Level 1 (`#`) - Top-level Sections
- **PREFACE** - Author's introduction
- **Chapter I**, **Chapter II**, etc. - Main chapters

### Level 2 (`##`) - Major Sections
- **CONTENTS** - Table of contents
- **THE ALPHABET** - Major chapter sections
- **RULES OF SANDHI** - Major chapter sections
- **ABBREVIATIONS USED IN THE WORK** - Reference sections

### Level 3 (`###`) - Subsections
- **I. SVARASANDHI** - Roman numeral subsections
- **II. HALSANDHI** - Chapter subdivisions
- **III. VISARGASANDHI** - Topical divisions

### Level 4 (`####`) - Detailed Sections
- **§ 1. Sanskrit, or the refined language...** - Numbered paragraphs
- **§ 2. The Devanāgarī alphabet...** - Rules and explanations
- **§ 18. By sandhi...** - Detailed grammar rules

## Document Structure Example

```markdown
# PREFACE
[Preface content...]

## CONTENTS
### I. The Alphabet ... ... ... 1
### II. Rules of Sandhi:— ... ... 11

# Chapter I.
## THE ALPHABET.
#### § 1. Sanskrit, or the refined language...
#### § 2. The Devanāgarī alphabet consists...

# CHAPTER II.
## RULES OF SANDHI.
### I. SVARASANDHI, OR THE COMBINATION OF FINAL AND INITIAL VOWELS.
#### § 19. If a simple vowel, short or long...
#### § 20. When a or ā is followed by...
```

## Navigation Features

### For Markdown Parsers
- Standard heading hierarchy (h1-h4)
- Consistent structure throughout
- Proper nesting of sections

### For Static Site Generators
- Auto-generated table of contents
- Section-based navigation
- Breadcrumb support

### For Document Readers
- Collapsible sections
- Quick jump to chapters
- Search within structure

## Sanskrit Notation

Sanskrit terms are tagged with `@[...]` syntax:
- `@[Pāṇini]` - Person names
- `@[Devanāgarī]` - Script/alphabet names
- `@[sandhi]` - Technical terms
- `@[सं]` - Devanagari characters

## Special Features

### Preserved Elements
- ✅ Footnotes with asterisks (*)
- ✅ Diacritical marks (ā, ī, ū, ṛ, ṃ, ḥ, ñ, ṭ, ḍ, ṇ, ś, ṣ)
- ✅ Mathematical/linguistic examples
- ✅ Tables and lists
- ✅ Cross-references to other sections

### Removed Elements
- ❌ Running headers (page headers from original book)
- ❌ Page numbers embedded in text
- ❌ OCR artifacts and noise
- ❌ Chunk metadata from processing
- ❌ Redundant section markers

## Usage Examples

### Generating Table of Contents
```bash
# Extract all headings for TOC
grep "^#" final_book.md
```

### Converting to HTML
```bash
# Using pandoc
pandoc final_book.md -o book.html --toc --toc-depth=4

# Using markdown-it
markdown-it final_book.md > book.html
```

### Converting to PDF
```bash
# Using pandoc with LaTeX
pandoc final_book.md -o book.pdf --toc --number-sections
```

### Viewing with Preview
```bash
# Most markdown viewers support navigation
# - VS Code: Outline view
# - GitHub: Auto-generated TOC
# - Obsidian: Document outline
```

## Processing Pipeline Summary

1. **OCR** (`ocr_pages.py`) - Extract text from PDF pages
2. **Chunking** (`create_chunks.py`) - Create 2-page overlapping chunks
3. **Cleanup** (`cleanup_chunks.sh`) - Fix OCR errors via Claude
4. **Aggregation** (`aggregate_cleaned_chunks.py`) - Combine and structure

### Final Output Quality
- ✅ Zero artifacts
- ✅ Proper hierarchy
- ✅ Consistent formatting
- ✅ Fully navigable
- ✅ Parser-compatible

## File Locations

- **Source**: `2015.105411.Higher-Sanskrit-Grammar.pdf`
- **Raw OCR**: `raw_pages/page_*.txt`
- **Chunks**: `chunks/chunk_*.txt`
- **Cleaned**: `structured_chapters/chunk_*_structured.md`
- **Final**: `final_complete_book.md` (when all chunks processed)

## Quality Metrics

- **Pages**: 729 pages total
- **Chunks**: 728 two-page chunks (1-page overlap)
- **Headings**: ~400+ structured headings
- **Sections**: ~300+ numbered sections (§)
- **Sanskrit Terms**: Thousands tagged with `@[...]`
