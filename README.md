# Kale's Sanskrit Grammar - OCR Digitization Project

High-quality OCR extraction of Kale's Higher Sanskrit Grammar (7th Edition, 1931) using dual OCR engines for maximum accuracy.

## Overview

This project digitizes Kale's Higher Sanskrit Grammar using a multi-engine OCR approach:

- **Google Cloud Vision API** - Excellent for Devanagari script recognition
- **Claude Vision (Anthropic)** - Superior for IAST diacriticals, mixed scripts, and complex layouts
- **Image Preprocessing** - Deskewing, contrast enhancement, noise reduction for optimal OCR quality

**Goal:** Extract all 972 rules and appendices with maximum accuracy for preservation and accessibility.

## Current Status

### Phase 1: Dual OCR Pipeline ✅ Complete

- ✅ Source PDF identified and verified (DLI 2015.105411, 7th Edition 1931)
- ✅ Image preprocessing pipeline implemented
- ✅ Google Vision OCR integration complete
- ✅ Claude Vision OCR integration complete
- ✅ Dual OCR batch processing pipeline complete
- ✅ **All 729 pages processed** with both engines
  - 729 pages successfully OCR'd with Google + Claude
  - Book content: pages 1-726 (726 pages)
  - Library metadata: pages 727-729 (3 pages)
  - ~$14 total cost for dual OCR run
  - Average confidence: 87%+

### Phase 2: OCR Reconciliation & Structuring ✅ Complete

- ✅ Implemented intelligent reconciliation (Claude compares Google + Claude OCR)
- ✅ **All 729 pages processed** with structured markdown output
  - Book content: 726 pages (pages 1-726)
  - Library metadata: 3 pages (pages 727-729)
- ✅ YAML front matter with metadata (rule numbers, topics, Pāṇini refs)
- ✅ Sanskrit terms tagged with proper IAST transliteration
- ✅ Standardized formatting (rule numbers, emphasis markers, footnotes)
- ✅ Content preservation validation (avg 99%+ accuracy)

Output: `structured_pages/` directory with 729 markdown files (726 book content + 3 metadata)

### Phase 3: Rule Extraction & Navigation

- [ ] Extract 972 individual rules from structured pages into `rules/rule_NNN.md`
- [ ] Structure and extract appendices into organized sections:
  - DHĀTUPĀṬHA (verb roots) - structured table with roots, classes, meanings
  - Gaṇapāṭha (lists) - organized by gaṇa number
  - Prosody sections - meter definitions and examples
  - Reference tables - declension/conjugation paradigms
  - Create `appendices/` directory with properly structured markdown
- [ ] Generate `TABLE_OF_CONTENTS.md` - markdown file with hyperlinked navigation
  - Extract section hierarchy from rule titles and YAML metadata
  - Organize by content structure (not pages): Alphabet, Sandhi, Declensions, etc.
  - Include rule numbers, titles, and brief descriptions
  - Add Pāṇini references and cross-references
  - Link to individual rule files and appendices
  - Simple markdown links (UI rendering handled in separate UI repo)
- [ ] Build comprehensive index and cross-references
- [ ] Create searchable word index from YAML `word_index` fields
- [ ] Validate against existing extraction from old-master branch

## Repository Structure

```
├── docs/                                # Documentation
│   ├── CODING_STANDARDS.md             # Code quality guidelines
│   ├── MARKDOWN_SPEC.md                # Output format specification
│   ├── SETUP_API_KEYS.md               # API configuration guide
│   ├── QUICK_START.md                  # Getting started guide
│   └── SOURCES.md                      # Source PDF information
├── scripts/                             # OCR processing pipeline
│   ├── google_vision_ocr_simple.py     # Google Vision module
│   ├── claude_vision_ocr.py            # Claude Vision module
│   ├── preprocess_image.py             # Image preprocessing
│   ├── dual_ocr.py                     # Main dual OCR orchestrator
│   ├── batch_ocr.py                    # Single-engine batch processor
│   ├── compare_quality.py              # Source quality comparison
│   ├── download_7th_edition_sources.py # Source acquisition
│   └── verify_7th_edition.py           # Edition verification
├── source/                              # Source PDFs (Git LFS tracked)
│   ├── 2015.105411.Higher-Sanskrit-Grammar.pdf
│   └── candidates/                      # 7th edition sources
│       ├── DLI_2015_IGNCA_Delhi.pdf    # Primary source (best quality)
│       ├── Official_7th_Edition_1931.pdf
│       └── xMqc_1931_Mulgaokar.pdf
├── ocr_output/                          # Phase 1 OCR results (not in git)
│   ├── google/                         # Google Vision results
│   │   ├── page_NNN.png                # Preprocessed page image
│   │   ├── page_NNN.txt                # OCR text output
│   │   └── page_NNN.json               # Full OCR response
│   └── claude/                         # Claude Vision results
│       ├── page_NNN.png                # Preprocessed page image
│       ├── page_NNN.txt                # OCR text output
│       └── page_NNN.json               # Full OCR response
├── structured_pages/                    # Phase 2 structured output (not in git)
│   ├── page_NNN.md                     # Structured markdown with YAML
│   └── page_NNN_validation.json        # Validation report
├── data/                                # Processing metadata
│   ├── processing_status.json          # Phase 2 progress tracking
│   └── consistency_data.json           # Sanskrit terms, citations index
├── quality_comparison.json              # Source quality analysis
├── .gitattributes                       # Git LFS configuration
├── .env.template                        # Environment variable template
└── README.md                            # This file
```

## Source Material

**Primary Source:** Digital Library of India, 2015.105411
**Edition:** 7th Edition (1931) - Final edition by M.R. Kale
**Publisher:** Gopal Narayen & Co., Bombay
**Pages:** 729 pages
**Quality:** 300 DPI scans, excellent condition

We verified multiple digitizations and selected DLI 2015 IGNCA Delhi as the primary source (90% quality win rate vs other sources).

## OCR Pipeline

### Preprocessing

Each page undergoes:

1. **Deskewing** - Correct rotated/skewed pages
2. **Border removal** - Remove scanning artifacts
3. **Noise reduction** - Median filter to clean up
4. **Contrast enhancement** - 1.3x boost for clarity
5. **Sharpness enhancement** - 1.2x boost for crisp text

### Dual OCR Execution

For each page:

1. Extract from PDF at 300 DPI
2. Apply preprocessing pipeline
3. Run **Google Vision OCR**
   - Optimized for Devanagari script
   - Language hints: Sanskrit, English
   - Returns text + confidence scores
4. Run **Claude Vision OCR**
   - Optimized for IAST diacriticals
   - Custom prompt for character-by-character transcription
   - Better at mixed scripts and complex layouts
5. Save both results (text, JSON, preprocessed image)

**Performance:** 20-28 seconds per page, ~$0.019 per page

### Why Dual OCR?

- **Google Vision** excels at Devanagari (धी, भू, सू)
- **Claude Vision** excels at IAST diacritics (ā, ī, ū, ṛ, ṃ, ḥ, ṭ, ḍ, ṇ, ś, ṣ)
- **Together** they provide complementary strengths for maximum accuracy
- Cost: ~$13.85 for entire 729-page book (one-time expense)

## Quick Start

### Prerequisites

```bash
# Install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install google-cloud-vision anthropic pdf2image pillow python-dotenv
```

### API Keys Setup

1. **Google Cloud Vision API**
   - Create project at https://console.cloud.google.com
   - Enable Cloud Vision API
   - Create API key
   - Add to `.env`: `GOOGLE_APPLICATION_CREDENTIALS=AIza...`

2. **Anthropic Claude API**
   - Get API key from https://console.anthropic.com
   - Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`

See [docs/SETUP_API_KEYS.md](docs/SETUP_API_KEYS.md) for detailed setup.

### Run OCR

```bash
# Process specific page range
python3 scripts/dual_ocr.py \
  --pdf source/candidates/DLI_2015_IGNCA_Delhi.pdf \
  --start 1 \
  --end 50 \
  --google-output ocr_output/google \
  --claude-output ocr_output/claude

# Process single page
python3 scripts/dual_ocr.py --pdf source/[...].pdf --pages 44
```

## Output Format

OCR results are saved in three files per page per engine:

- `page_NNN.txt` - Plain text transcription
- `page_NNN.json` - Full OCR response with metadata
- `page_NNN.png` - Preprocessed image used for OCR

Example structure:

```
ocr_output/
  google/
    page_001.txt    # "INTRODUCTION\n\nSanskrit grammar..."
    page_001.json   # {"text": "...", "confidence": 0.94, ...}
    page_001.png    # Preprocessed image
  claude/
    page_001.txt    # Character-by-character transcription
    page_001.json   # {"text": "...", "usage": {...}}
    page_001.png    # Same preprocessed image
```

## Next Phase: Intelligent Merge & Extraction

The next phase will:

1. **Merge OCR results** - Use Claude AI to compare Google + Claude OCR, selecting best parts from each
2. **Parse rule boundaries** - Identify §1 through §972
3. **Extract rules** - Individual markdown files with proper formatting
4. **Extract appendices** - DHATUKOSHA, Prosody sections
5. **Validate** - Compare against old-master branch extraction

## Cost Analysis

- **Google Vision:** $1.50 per 1,000 pages = ~$1.09 for 729 pages
- **Claude Vision:** ~$12-15 for 729 pages (varies by response length)
- **Total:** ~$13.85 one-time cost
- **Quality:** Dual-engine accuracy worth the investment

## Documentation

- [Coding Standards](docs/CODING_STANDARDS.md) - Code quality guidelines
- [Markdown Specification](docs/MARKDOWN_SPEC.md) - Output format rules
- [API Setup Guide](docs/SETUP_API_KEYS.md) - Configure Google + Anthropic APIs
- [Quick Start](docs/QUICK_START.md) - Get running quickly
- [Sources](docs/SOURCES.md) - Information about source PDFs

## Branches

- **main** - Current OCR pipeline work (this branch)
- **old-master** - Previous extraction with 972 rules already extracted
- **ocr-code-only** - Clean code-only branch without data files

## License

This project digitizes a public domain work (Kale's Sanskrit Grammar, 1931) for preservation and accessibility.

## References

- Kale, M.R. (1931). _A Higher Sanskrit Grammar_. 7th Edition. Gopal Narayen & Co., Bombay.
- Digital Library of India: 2015.105411
- Google Cloud Vision API: https://cloud.google.com/vision
- Anthropic Claude API: https://anthropic.com
