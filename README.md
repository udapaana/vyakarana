# Kale's Sanskrit Grammar - OCR Improvement Project

Extract Kale's Higher Sanskrit Grammar with maximum accuracy using:

1. **Multi-pass OCR** - Run both Google Vision OCR and Claude Vision OCR on each page
2. **Intelligent merging** - Use Claude AI to compare and merge both OCR results for best accuracy
3. **Structured extraction** - Extract 972 rules and appendices into clean markdown format

## Contents

- **972 rules** from Kale's original text, individually extracted
- **Appendices** (DHATUKOSHA, Prosody, etc.)
- Clean markdown format with YAML front matter
- IAST transliteration and Devanagari in structured notation
- Automated OCR cleanup pipeline using Claude AI

## Architecture

### Phase 1: Multi-Pass OCR

For each page in the source PDF:

1. Extract page as high-resolution image (300 DPI)
2. Run **Google Vision OCR** (excellent for Devanagari script)
3. Run **Claude Vision OCR** (excellent for mixed scripts, tables, IAST diacritics)
4. Use **Claude AI** to intelligently merge both results, selecting best parts from each

### Phase 2: Structured Extraction

- Parse merged OCR output to identify rule boundaries (§1 - §972)
- Extract each rule into individual markdown file
- Extract appendices (DHATUKOSHA, Prosody, etc.)
- Apply formatting standards (IAST in `@[...]`, Devanagari in `@deva[...]`)

### Phase 3: Validation & Cleanup

- Compare against existing extraction from master branch
- Identify and fix remaining OCR errors
- Validate all 972 rules are present and correctly formatted

## Source

**in.ernet.dli.2015.105411** - 729 pages, IGNCA Delhi, 300 DPI

- Downloaded from Internet Archive
- Path: `source/2015.105411.Higher-Sanskrit-Grammar.pdf`

## Directory Structure

```
├── source/                              # Source PDF
│   └── 2015.105411.Higher-Sanskrit-Grammar.pdf
├── scripts/                             # Processing pipeline
│   ├── google_vision_ocr.py            # Google Vision OCR module
│   ├── claude_vision_ocr.py            # Claude Vision OCR module
│   ├── merge_results.py                # Intelligent merging with Claude
│   ├── extract_rules.py                # Extract individual rules
│   └── extract_appendices.py           # Extract appendices
├── images/                              # Extracted page images (300 DPI)
│   ├── page_001.png
│   ├── page_002.png
│   └── ...
├── ocr_output/
│   ├── google/                         # Google Vision OCR results
│   │   ├── page_001.txt
│   │   └── ...
│   ├── claude/                         # Claude Vision OCR results
│   │   ├── page_001.txt
│   │   └── ...
│   └── merged/                         # Merged final OCR
│       ├── page_001.txt
│       └── ...
├── final/                               # Final extracted content
│   ├── rules/                          # 972 rules
│   │   ├── 001.md
│   │   ├── 002.md
│   │   └── ...
│   └── appendices/                     # Appendices
│       ├── dhatukosha.md
│       └── prosody.md
├── CODING_STANDARDS.md                  # Coding principles
├── MARKDOWN_SPEC.md                     # Markdown formatting spec
└── README.md                            # This file
```

## Coding Standards

All code in this project follows the standards documented in [CODING_STANDARDS.md](./CODING_STANDARDS.md).

Key principles:

- **Deep modules**: Simple interfaces, users specify what, not how
- **Dependency injection**: Pass in engines rather than hardcoding
- **Comments explain why**: Why we use multiple engines, why certain merging strategies
- **Testable**: Each component can be tested in isolation

## Markdown Format

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

See [MARKDOWN_SPEC.md](./MARKDOWN_SPEC.md) for full specification.

## Usage

### Step 1: Run multi-pass OCR pipeline

```bash
python3 scripts/run_ocr_pipeline.py --start-page 1 --end-page 729
```

This will:

1. Extract each page as high-resolution image (300 DPI)
2. Run Google Vision OCR on each page
3. Run Claude Vision OCR on each page
4. Use Claude AI to intelligently merge both results
5. Save merged OCR output

### Step 2: Extract structured content

```bash
python3 scripts/extract_rules.py
python3 scripts/extract_appendices.py
```

This will parse the merged OCR output and extract:

- 972 individual rules into `final/rules/`
- Appendices into `final/appendices/`

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

- [x] Select source PDF (in.ernet.dli.2015.105411)
- [ ] Implement Google Vision OCR module
- [ ] Implement Claude Vision OCR module
- [ ] Implement intelligent merge module
- [ ] Implement main orchestration script
- [ ] Process all 729 pages with multi-pass OCR
- [ ] Extract 972 rules from merged output
- [ ] Extract appendices (DHATUKOSHA, Prosody)
- [ ] Validate against master branch

## References

- Internet Archive search results for Kale's Grammar
- Google Cloud Vision API documentation
- Anthropic Claude Vision API documentation
- [Coding Standards](./CODING_STANDARDS.md)
- [Markdown Specification](./MARKDOWN_SPEC.md)
