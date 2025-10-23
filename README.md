# Kale's Higher Sanskrit Grammar - Digital Edition Project

**Source:** M. R. Kale, "A Higher Sanskrit Grammar" (Bombay, 1894)
**Goal:** Create a machine-readable, AST-parseable digital edition
**Status:** v7 Complete → Starting v8 (AST-ready semantic markup)

## Current Version

**`output/kales_sanskrit_grammar_v7.md`** - Latest cleaned version (99% accurate)
**Next:** v8 with semantic markup for AST generation (see `MARKUP_SPECIFICATION.md`)

## Version History

All intermediate versions are preserved in `versions_archive/` for potential reprocessing:

- **v1**: `kales_sanskrit_grammar_v1_raw_ocr.md` - Raw OCR aggregation from PDF (19,145 lines)
- **v2**: `kales_sanskrit_grammar_v2_standardized.md` - First standardization pass
- **v3**: `kales_sanskrit_grammar_v3_standardized_improved.md` - Improved standardization (18,733 lines)
- **v4**: `kales_sanskrit_grammar_v4_nlp_standardized.md` - NLP-based standardization
- **v5**: `kales_sanskrit_grammar_v5_iast.md` - IAST standardization with Sanskrit term mapping
- **v6**: `kales_sanskrit_grammar_v6_spacy_improved.md` - spaCy-based improvements with intelligent paragraph merging
- **v7**: `kales_sanskrit_grammar_v7.md` - Latest polished version (18,080 lines)

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
├── source/                                # Source materials
│   └── 2015.105411.Higher-Sanskrit-Grammar.pdf
├── output/                                # Generated outputs
│   └── kales_sanskrit_grammar_v7.md
├── versions_archive/                      # All intermediate versions (v1-v6)
├── scripts/
│   ├── ocr/                              # PDF → Text extraction
│   ├── processing/                       # Cleaning & standardization
│   └── validation/                       # (Future) AST validation
├── docs_archive/                          # Process documentation
├── MARKUP_SPECIFICATION.md                # **READ THIS** - v8 format spec
└── README.md                              # This file
```

**Note:** Raw OCR data (`raw_pages/`, `chunks/`, `structured_chapters/`) retained but not shown. Can be regenerated from source PDF.

## Quality Metrics (v7)

- **Completeness**: 100% (all 728 pages processed)
- **Structure**: 85% (proper heading hierarchy, formatted TOC)
- **IAST Standardization**: 70% (major Sanskrit terms converted)
- **Sanskrit Tagging**: 65% (common terms tagged with `@[...]`)
- **Cleanliness**: 80% (OCR artifacts removed)
- **Line Count**: 18,080 lines (optimized from 19,145 original)

## Next Steps: v7 → v8 Transformation

### v8 Goals (AST-Ready Semantic Markup)

- 🎯 **Machine-readable structure** for AST generation
- 🎯 **Consistent Sanskrit markup** (`@[...]` inline, `@:...:@` blocks)
- 🎯 **Standardized citations** (`@cite{Work:Reference}`)
- 🎯 **Typed grammar rules** (`@rule{type: "sandhi.vowel.guna"}`)
- 🎯 **Structured examples** (`@[a] + @[b] → @[c]`)
- 🎯 **Metadata for tables** (`@declension{word: "rāma"}`)

### Read the Specification

See **[`MARKUP_SPECIFICATION.md`](MARKUP_SPECIFICATION.md)** for complete format details before starting section processing.

### Processing Approach

1. Extract sections from v7 by chapter/topic
2. Apply semantic markup via Claude (section by section)
3. Validate parseability
4. Reassemble into v8
5. Generate AST/JSON output

## Usage

**Current v7** can be used for:

- Digital reading and research
- Text analysis and linguistic studies
- Integration with Sanskrit learning tools

**Future v8** will enable:

- Programmatic querying of grammar rules
- AST-based analysis and transformations
- Database storage with relationships
- Interactive web applications
- Multiple output formats (JSON, GraphQL, SQL)
