# Project Folder Structure

This document describes the standardized folder naming convention that reflects the three-phase OCR extraction pipeline.

## Pipeline Overview

The project processes Kale's Higher Sanskrit Grammar through three phases:

1. **Phase 1: OCR** - Extract text from PDF pages
2. **Phase 2: Structuring** - Convert OCR to structured markdown
3. **Phase 3: Rule Extraction** - Extract individual grammar rules

## Directory Structure

```
/
├── phase1_ocr/              # Phase 1: OCR Output
│   ├── claude/              # Claude Vision OCR
│   │   ├── page_001.png     # Rendered page images (300 DPI)
│   │   ├── page_001.txt     # OCR text output
│   │   ├── page_001.json    # OCR metadata
│   │   └── ...
│   └── google/              # Google Vision OCR
│       ├── page_001.png     # Rendered page images
│       ├── page_001.txt     # OCR text output
│       └── ...
│
├── phase2_structured/       # Phase 2: Structured Pages
│   ├── page_001.md          # Structured markdown with YAML frontmatter
│   ├── page_002.md
│   ├── ...
│   ├── page_013a.md         # Pages with letter suffixes (inserted pages)
│   ├── page_013b.md
│   └── ...
│
├── phase3_rules/            # Phase 3: Extracted Grammar Rules
│   ├── rule_001.md          # Individual rule files
│   ├── rule_002.md
│   └── ...
│
├── source/                  # Source PDF files
│   └── candidates/
│       ├── Official_7th_Edition_1931.pdf
│       ├── DLI_2015_IGNCA_Delhi.pdf
│       └── xMqc_1931_Mulgaokar.pdf
│
├── scripts/                 # All scripts and utilities
│   ├── ai/                  # AI-powered extraction scripts
│   ├── extraction/          # Extraction utilities
│   ├── processing/          # Processing scripts
│   └── utilities/           # Utility scripts
│
├── docs/                    # All documentation
├── data/                    # Processing data and metadata
├── logs/                    # Extraction logs
└── appendices/              # Appendix content
```

## Phase Completeness Status

### Phase 1: OCR (✅ COMPLETE)
- **Input**: PDF pages from source/candidates/
- **Output**: phase1_ocr/claude/ and phase1_ocr/google/
- **Status**: All 731 pages have complete OCR
  - 731 Claude PNGs, TXTs, JSONs
  - 731 Google PNGs, TXTs

### Phase 2: Structuring (✅ COMPLETE)
- **Input**: phase1_ocr/
- **Output**: phase2_structured/
- **Status**: All 972 rules present in 731 structured pages
  - Includes newly added pages 013a, 013b (§ 7-10)
  - YAML frontmatter with metadata
  - Markdown content with @deva[] and @[] tags

### Phase 3: Rule Extraction (⚠️ IN PROGRESS - 7.4%)
- **Input**: phase2_structured/
- **Output**: phase3_rules/
- **Status**: 72/972 rules extracted (7.4% complete)
  - 900 rules remaining
  - Individual rule markdown files

## Key Scripts

All scripts have been updated to use the new folder names:

- `validate_all_rules.py` - Validates all 972 rules are present
- `parallel_extract.sh` - Runs parallel Phase 3 extraction
- `scripts/ai/parallel_extractor.py` - Parallel extraction worker
- `scripts/ai/batch_sequential.py` - Sequential extraction
- `scripts/processing/process_batch.py` - Batch processing for Phase 2
- `scripts/utilities/structure_missing_ocr_files.py` - Structure OCR output

## Migration Notes

**Previous Names** → **New Names**:
- `ocr_output/` → `phase1_ocr/`
- `structured_pages/` → `phase2_structured/`
- `rules/` → `phase3_rules/`

All code references have been updated to use the new naming convention.

## Usage

### Validate All Rules
```bash
python3 validate_all_rules.py
```

### Run Phase 3 Extraction
```bash
./parallel_extract.sh
```

### Check Pipeline Status
```bash
# Count Phase 1 OCR files
ls phase1_ocr/claude/*.png | wc -l

# Count Phase 2 structured pages
ls phase2_structured/*.md | wc -l

# Count Phase 3 extracted rules
ls phase3_rules/rule_*.md | wc -l
```

## Benefits of New Structure

1. **Clear Pipeline Flow**: Folder names explicitly show the three-phase pipeline
2. **Self-Documenting**: Anyone can understand the workflow by looking at folder names
3. **Consistent Naming**: All phases follow the same `phaseN_description` pattern
4. **Easy Navigation**: Quickly identify which phase's output you're looking at
5. **Script Clarity**: Code referencing these folders is more readable
