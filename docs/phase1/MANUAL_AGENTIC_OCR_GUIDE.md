# Manual Agentic OCR Conversion Guide

**Project**: Kale's Higher Sanskrit Grammar (1931 Edition) - Phase 1 OCR  
**Last Updated**: 2025-11-04  
**Current Progress**: Pages 1-230 completed (out of 732 total images)

---

## Table of Contents

1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [File Organization](#file-organization)
4. [Dual Numbering System](#dual-numbering-system)
5. [OCR Workflow](#ocr-workflow)
6. [File Format Specifications](#file-format-specifications)
7. [Current Status](#current-status)
8. [How to Continue in a New Thread](#how-to-continue-in-a-new-thread)
9. [Quality Standards](#quality-standards)

---

## Overview

This project involves manually transcribing Kale's Higher Sanskrit Grammar (official_1931 edition) using Claude as an interactive OCR agent. The goal is to create high-quality, searchable text files from scanned images of the original 1931 publication.

### Why Manual Agentic OCR?

- **Complex Scripts**: The source material contains Devanagari script, IAST transliteration, and English text
- **Specialized Content**: Sanskrit grammatical terminology, Pāṇini sūtra references, and technical linguistic notation
- **High Accuracy**: Manual verification ensures better quality than automated OCR for specialized academic content
- **Structured Output**: Consistent formatting with metadata tracking

---

## Project Structure

```
/Users/skmnktl/Downloads/ocr/
├── phase1_ocr/
│   ├── images/
│   │   └── official_1931/           # Source PNG images (1.png - 732.png)
│   └── sources/
│       └── official_1931/           # OCR output (.txt and .json pairs)
├── archive/                         # Old scripts and documentation
├── docs/                            # Project documentation
├── scripts/                         # Utility scripts
└── MANUAL_AGENTIC_OCR_GUIDE.md     # This file
```

---

## File Organization

### Source Images
- **Location**: `/phase1_ocr/images/official_1931/`
- **Format**: PNG files numbered sequentially (1.png, 2.png, ..., 732.png)
- **Total**: 732 images covering the entire book

### OCR Output
- **Location**: `/phase1_ocr/sources/official_1931/`
- **Format**: Paired files for each page:
  - `NNN.txt` - Plain text transcription
  - `NNN.json` - Metadata file

---

## Dual Numbering System

**CRITICAL**: This project maintains TWO numbering systems:

### 1. File Path Numbers (Sequential)
- **Purpose**: Maintain sequence and map images to output files
- **Format**: Sequential integers (1, 2, 3, ..., 230, 231, ...)
- **Example**: `211.png` → `211.txt` + `211.json`
- **Never skip**: Files are numbered continuously regardless of content

### 2. Internal Page Numbers (Book Pages)
- **Purpose**: Identify the actual page number printed in the book
- **Format**: Varies by section:
  - Front matter: Roman numerals (i, ii, iii, iv, ...)
  - Main content: Arabic numerals (1, 2, 3, ..., 216, ...)
  - Some pages have no numbers (title pages, blank pages)
- **Example**: File `211.txt` contains internal page `197`
- **Recorded**: At the top of each `.txt` file as `[Internal page: X]`

### Why Both?

- **File numbers**: Ensure no images are skipped or lost
- **Internal pages**: Identify gaps in the original book, cross-reference with physical copies
- **Gap detection**: If file 50 has internal page 35, we know pages 36-49 are front matter or special pages

---

## OCR Workflow

### Batch Processing Strategy

**Recommended Approach**: Process in batches of 5 pages

1. **User provides images**: Links to next batch (e.g., 231.png - 250.png)
2. **Claude processes in batches of 5**:
   - Batch 1: Files 231-235
   - Batch 2: Files 236-240
   - Batch 3: Files 241-245
   - Batch 4: Files 246-250
3. **Output for each page**: Create both `.txt` and `.json` files
4. **Progress tracking**: Use TodoWrite tool to track each batch

### Step-by-Step Process

For each page:

1. **Read the image**: Examine the scanned page carefully
2. **Identify internal page number**: Check header/footer for printed page number
3. **Transcribe content**:
   - Preserve all text formatting (headers, indentation, spacing)
   - Maintain Devanagari script exactly as shown
   - Preserve IAST transliteration with proper diacritics
   - Keep English explanatory text
   - Include all grammatical notation and symbols
4. **Create `.txt` file**:
   - Start with `[Internal page: X]` marker
   - Follow with transcribed content
5. **Create `.json` metadata file**:
   - Include page_number, source, content_type, ocr_method, timestamp

---

## File Format Specifications

### Text File Format (`.txt`)

```
[Internal page: 197]

TADDHITA AFFIXES.                                                  197

[Rest of transcribed content follows...]
```

**Key Requirements**:
- First line: `[Internal page: X]` where X is the printed page number
  - Use `[Internal page: none]` if page has no number
  - Use `[Internal page: iv]` for Roman numerals
- Preserve exact spacing and indentation
- Maintain line breaks as they appear
- Include all diacritics and special characters
- Keep headers, footers, and page numbers as shown

### JSON Metadata Format (`.json`)

```json
{
  "page_number": "211",
  "source": "official_1931",
  "content_type": "chapter_9_taddhita_affixes_section1",
  "ocr_method": "claude_interactive",
  "timestamp": "2025-11-04"
}
```

**Fields**:
- `page_number`: File number (as string)
- `source`: Always "official_1931"
- `content_type`: Descriptive label for content (use underscores, be specific)
- `ocr_method`: Always "claude_interactive"
- `timestamp`: Date of OCR (YYYY-MM-DD format)

---

## Current Status

### Progress Summary
- **Completed**: Pages 1-230 (files + internal page markers)
- **Remaining**: Pages 231-732 (502 pages)
- **Percentage**: 31.4% complete

### Last Completed Page
- **File**: 230.txt / 230.json
- **Internal Page**: 216
- **Content**: Beginning of Chapter X (Gender)
- **Section**: Transitioning from Taddhita Affixes to Gender rules

### Next Steps
- **Resume from**: File 231.png
- **Expected internal page**: ~217 (verify when processing)
- **Content**: Continuation of Chapter X (Gender)

### Content Coverage (Completed)

Pages 1-230 cover:
- **Front Matter**: Title pages, copyright, preface (pages 1-14)
- **Chapter I**: The Alphabet (pages 15-25, approximately)
- **Chapter II**: Rules of Sandhi (pages 26-60, approximately)
- **Chapter III**: Declension (pages 61-90, approximately)
- **Chapter IV**: Conjugation (pages 91-140, approximately)
- **Chapter V**: Participles (pages 141-150, approximately)
- **Chapter VI**: Indeclinables (pages 151-160, approximately)
- **Chapter VII**: Verbal Derivatives (pages 161-170, approximately)
- **Chapter VIII**: Nominal Compounds (pages 171-190, approximately)
- **Chapter IX**: Taddhita Affixes - Sections I-III (pages 191-215, approximately)
- **Chapter X**: Gender - Beginning (page 216)

---

## How to Continue in a New Thread

When starting a new Claude Code session to continue this work:

### 1. Provide This Context

Share this document (`MANUAL_AGENTIC_OCR_GUIDE.md`) with Claude and provide:

```
We're continuing manual agentic OCR work on Kale's Sanskrit Grammar (1931).

Current progress: Pages 1-230 completed
Next batch: Starting from page 231
Please read MANUAL_AGENTIC_OCR_GUIDE.md for full context.

[Provide image links for next batch, e.g., 231.png - 250.png]
```

### 2. Claude Should:

1. Read this guide to understand the workflow
2. Check the last completed file to verify continuity:
   ```bash
   ls /Users/skmnktl/Downloads/ocr/phase1_ocr/sources/official_1931/*.txt | tail -1
   cat /Users/skmnktl/Downloads/ocr/phase1_ocr/sources/official_1931/230.txt | head -5
   ```
3. Confirm starting point (file 231, internal page ~217)
4. Process images in batches of 5
5. Create `.txt` and `.json` pairs for each page
6. Update this document's "Current Status" section when batch is complete

### 3. Quality Checks

Before ending a session, verify:
- All `.txt` files have `[Internal page: X]` markers
- All `.txt` files have corresponding `.json` files
- File numbers are sequential with no gaps
- Internal page numbers are tracked and make sense

---

## Quality Standards

### Text Accuracy
- **Devanagari**: Must be pixel-perfect transcription
- **IAST**: All diacritics must be correct (ā, ī, ū, ṛ, ṃ, ḥ, ś, ṣ, etc.)
- **English**: Standard spelling and grammar as in original
- **Numbers**: Preserve exactly as shown (including section numbers)

### Formatting Preservation
- **Headers**: Maintain chapter/section headers with original spacing
- **Indentation**: Keep all indentation levels (especially for examples)
- **Tables**: Preserve tabular layouts using spacing
- **Special notation**: Keep all grammatical notation (parentheses, brackets, etc.)

### Metadata Accuracy
- **File numbers**: Must match image filename
- **Internal pages**: Must match printed page number in image
- **Content type**: Should be descriptive and consistent
- **Timestamps**: Use current date in YYYY-MM-DD format

---

## Common Issues and Solutions

### Issue: Mixed Scripts Not Rendering
**Solution**: Ensure UTF-8 encoding is maintained in all `.txt` files

### Issue: Internal Page Number Not Visible
**Solution**: Check header/footer, margins. Use `[Internal page: none]` if truly absent

### Issue: Complex Devanagari Ligatures
**Solution**: Take time to identify correct Unicode characters; consult references if needed

### Issue: Unclear Layout/Spacing
**Solution**: Use best judgment to preserve visual hierarchy; document ambiguities in notes

---

## Tools and Resources

### Unicode References
- Devanagari Unicode Chart: U+0900 to U+097F
- IAST diacritics: ā ī ū ṛ ṝ ḷ ḹ ṃ ḥ ś ṣ ñ

### Verification
- Cross-reference with physical book when possible
- Check internal page numbers for continuity
- Verify file sequence has no gaps

### Command-Line Checks

```bash
# Count completed pages
ls /Users/skmnktl/Downloads/ocr/phase1_ocr/sources/official_1931/*.txt | wc -l

# Check last completed file
ls /Users/skmnktl/Downloads/ocr/phase1_ocr/sources/official_1931/*.txt | tail -1

# Verify all .txt files have .json pairs
cd /Users/skmnktl/Downloads/ocr/phase1_ocr/sources/official_1931/
for f in *.txt; do [ ! -f "${f%.txt}.json" ] && echo "Missing: ${f%.txt}.json"; done

# Check for internal page markers
grep -L "^\[Internal page:" *.txt
```

---

## Notes for Future Sessions

### Session Continuity
- Always start by reading this guide
- Verify the last completed file number
- Check internal page continuity
- Use TodoWrite tool to track progress within session

### Updating This Document
At the end of each major batch (e.g., every 50 pages), update:
- **Current Status** section
- **Last Completed Page** details
- **Content Coverage** if new chapters/sections covered

### Long-Term Goals
- Complete all 732 pages
- Maintain consistent quality throughout
- Generate final statistics report upon completion
- Create index of internal page to file number mapping

---

## Contact and Issues

For questions or issues with this OCR project:
- Check this guide first
- Verify file formats match specifications
- Ensure dual numbering system is maintained
- Document any anomalies or special cases encountered

---

**Document Version**: 1.0  
**Created**: 2025-11-04  
**Last Updated**: 2025-11-04
