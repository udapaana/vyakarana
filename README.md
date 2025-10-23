# Kale's Higher Sanskrit Grammar - OCR Digitization Project

This repository contains the digitized version of Kale's 'A Higher Sanskrit Grammar' (1931).

## Current Version

**`kales_sanskrit_grammar_v7_final.md`** - Latest cleaned and processed version

## Version History

All intermediate versions are preserved in `versions_archive/` for potential reprocessing:

- **v1**: `kales_sanskrit_grammar_v1_raw_ocr.md` - Raw OCR aggregation from PDF (19,145 lines)
- **v2**: `kales_sanskrit_grammar_v2_standardized.md` - First standardization pass
- **v3**: `kales_sanskrit_grammar_v3_standardized_improved.md` - Improved standardization (18,733 lines)
- **v4**: `kales_sanskrit_grammar_v4_nlp_standardized.md` - NLP-based standardization
- **v5**: `kales_sanskrit_grammar_v5_iast.md` - IAST standardization with Sanskrit term mapping
- **v6**: `kales_sanskrit_grammar_v6_spacy_improved.md` - spaCy-based improvements with intelligent paragraph merging
- **v7**: `kales_sanskrit_grammar_v7_final.md` - Final polished version (18,080 lines)

## Processing Pipeline

### Initial OCR Pipeline

1. `ocr_pages.py` - Extract pages from PDF via Tesseract OCR (eng+san)
2. `create_chunks.py` - Create 2-page overlapping chunks for processing
3. `cleanup_chunks.sh` - Semantic cleanup via Claude CLI
4. `aggregate_cleaned_chunks.py` - Aggregate chunks into complete book

### Standardization Scripts

5. `standardize_format.py` - First cleanup attempt
6. `standardize_format_v2.py` - Improved cleanup with better paragraph logic
7. `nlp_standardizer.py` - spaCy proof of concept
8. `nlp_standardizer_v2.py` - Production spaCy version
9. `fast_iast_converter.py` - Fast IAST converter (0.4s runtime)
10. `claude_spacy_improver.py` - Final intelligent processing with spaCy

## Documentation

- `STRUCTURE.md` - Book structure and organization
- `QUALITY_REPORT.md` - Quality metrics and improvements applied to final version
- `docs_archive/` - Older documentation from intermediate processing stages

## Repository Structure

```
ocr/
├── kales_sanskrit_grammar_v7_final.md    # Current version
├── versions_archive/                      # All intermediate versions (v1-v6)
├── docs_archive/                          # Process documentation
├── chunks/                                # OCR processing chunks
├── cleaned_chunks/                        # Cleaned chunks from Claude
├── *.py                                   # Processing scripts
├── STRUCTURE.md                           # Book structure
├── QUALITY_REPORT.md                      # Quality metrics
└── README.md                              # This file
```

## Quality Metrics (v7)

- **Completeness**: 100% (all 728 pages processed)
- **Structure**: 85% (proper heading hierarchy, formatted TOC)
- **IAST Standardization**: 70% (major Sanskrit terms converted)
- **Sanskrit Tagging**: 65% (common terms tagged with `@[...]`)
- **Cleanliness**: 80% (OCR artifacts removed)
- **Line Count**: 18,080 lines (optimized from 19,145 original)

## Usage

The final version can be used for:

- Digital reading and research
- Text analysis and linguistic studies
- Integration with Sanskrit learning tools
- Further processing and enhancement

All intermediate versions are preserved in case reprocessing is needed with different parameters or improved tools.
