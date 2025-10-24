# Kale's Sanskrit Grammar - OCR Improvement

OCR## digitizationProject and structured extraction of

Extract ContentsKale'sHigher Sanskrit Grammar with maximum accuracy using:
1. **Multiple source digitizations** - Find the best quality image for each page
2. **Multiple OCR engines** - Google Vision OCR + Claude Vision OCR
3. **Intelligent merging** - Use Claude to compare and merge results for best accuracy

- **966 rules** from Kale's original text, individually extracted
- Clean markdown format with YAML front matter
- IAST transliteration and Devanagari in structured notation
- Automated OCR cleanup pipeline using Claude AI
##Architecture###Phase1: Source Collection
- Find all available digitizations of Kale's Grammar on Archive.org
- Download multiple versions (found 4+ different digitizations)
- Compare image quality for each page across sources
- Select best source image for each page###Phase2:Multi-PassOCR
-RunGoogle Vision OCR on each page (excellentDevanagari)
-Run Claude Vision OCR on each page (excellent for mixed scripts, tables, IAST diacritics)
- Use Claude to intelligently merge the two results### Phase 3: Validation & Cleanup
- Compare against existing extraction from master branch
- Identify and fix remaining issues
- Extract appendices (DHATUKOSHA, Prosody, etc.)
KnownDigitizationsFromInternetArchive:**inernet.dli.2015.105411**729,IGNCADelhicurrent source**HigherSanskritGrammarKale7thEdition**7thEdition1931,OCRedwithbookmarks**highersanskritgr00kaleuoft**1961edition,714pages,University of Toronto**gsshighersanskritgr0000mrka**1972edition,738pages,Motilal Banarsidass## Directory Structure

```
├── raw_pages/           # Original OCR text files (729 pages)
├── output/              # Processed markdown (v7)
├── rules/               # Extracted rules (001.md - 972.md)
├── rules_cleaned/       # Claude-cleaned rules (in progress)
├── scripts/             # Processing scripts
│   ├── extract_simple.py
│   ├── process_rules_batch.py
│   └── processing/      # Section extraction scripts
├── MARKDOWN_SPEC.md     # Formatting specification
└── PROCESSING_READY.md  # Processing guide
-improvements-v2                    OriginalPDFs├       # Current source (729 pages)│   7th_edition_1931.pdf  Todownload
│   ├── toronto_1961.pdf      # To download1972_editionpdf      Todownload│   ├── download_sources.py   # Download all digitizations
│   ├── compare_quality.py    # Compare image quality across sources
│   ├── select_best_images.py # Select best source for each page
│   ├── google_vision_ocr.py  # Google Vision OCR module
│   ├── claude_vision_ocr.py  # Claude Vision OCR module
│   └── merge_results.py      # Intelligent merging with Claude
├── images/                    # Selected best images for each page
│   ├── page_001.png
│   ├── page_002.png
│   └── ...
├── ocr_output/
│   ├── google/               # Google Vision results
│   ├── claude/               # Claude Vision results
│   └── merged/               # Final merged results
├── CODING_STANDARDS.md       # Coding principles for this project
└── README.md                 # This file
```

#### ExtractionCoding StatusStandards

✅All **966/966code rules extracted**in this project follows the standards documented in [CODING_STANDARDS.md](6 rule numbers don't exist in original./CODING_STANDARDS.md).

##Key MarkdownprinciplesDeepmodulessimple interfaces**: Users specify what, not howDependency injectionPassinenginesrather than hardcodingCommentsexplain whyWhy we use multiple engineswhycertainmergingstrategies
-**Testable**: Each component can be tested in isolation

Each rule file follows this structure:

```markdown
---
rule: §N
---

[Rule content with IAST in @[...] and Devanagari in @deva[...]]
```

### Notation
- **IAST**: `@[saṃskṛta]`, `@[pāṇini]`, `@[guṇa]`
- **Devanagari**: `@deva[संस्कृत]`, `@deva[पाणिनि]`, `@deva[गुण]`

## Processing

Process rules through Claude for cleanup:

```bash
# Test batch
python3 scripts/process_rules_batch.py 1 10

# Process in batches
python3 scripts/process_rules_batch.py 1 100
python3 scripts/process_rules_batch.py 101 200
```

See### `PROCESSING_READY.md`Step1 detailed instructions. Download all source digitizations
```bash
python scripts/download_sources.py
```
## Non###existent RulesStep2:Compareselectbest images```bash
pythonscripts/compare_quality.py
pythonscripts/select_best_images.py
```
The### Step 3: Run multi-pass OCR
```bash
python scripts/run_multipass_ocr.py --start-page 1 --end-page 729
```

This will:
1. Run Google Vision OCR on each page
2. Run Claude Vision OCR on each page
3. Use Claude to merge results intelligently
4. Output final markdown files

## Environment Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install google-cloud-vision anthropic pdf2image pillow

# Set API keys
export GOOGLE_APPLICATION_CREDENTIALS="path/to/google-credentials.json"
export ANTHROPIC_API_KEY="your-api-key"
```

## Progress Tracking

- [ ] Download all 4 digitizations
- [ ] Compare image quality across sources
- [ ] Select best source for each page
- [ ] Implement Google Vision OCR module
- [ ] Implement Claude Vision OCR module
- [ ] Implement intelligent merge module
- [ ] Process all 729 pages
- [ ] Extract appendices
- [ ] Validate against master branch

## References

- Internet Archive search results for Kale's Grammar
- Google Cloud Vision API documentation
- Anthropic Claude Vision API documentation
- [Coding Standards](./CODING_STANDARDS.md)
