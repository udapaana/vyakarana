# Scripts Documentation

This directory contains all processing scripts organized by function. Most scripts were used for specific one-off tasks during the multi-phase pipeline.

## Core Scripts by Phase

### Phase 1: Raw OCR Extraction

**Primary Scripts:**
- `google_vision_ocr_simple.py` - Google Cloud Vision OCR integration
- `claude_vision_ocr.py` - Claude Vision OCR integration (DEPRECATED - use ai/cli.py)
- `preprocess_image.py` - Image preprocessing (deskew, denoise, enhance)
- `dual_ocr.py` - Main dual-engine OCR orchestrator
- `batch_ocr.py` - Single-engine batch processor
- `ocr_official_1931.py` - Process Official 1931 source

**Support Scripts:**
- `extract_source_images.py` - Extract page images from PDF
- `download_7th_edition_sources.py` - Download source PDFs
- `verify_7th_edition.py` - Verify edition and quality
- `compare_quality.py` - Compare quality across sources

### Phase 2: Structuring

**AI-Assisted Extraction (ai/ subdirectory):**
- `ai/cli.py` - Main CLI for AI-assisted extraction
- `ai/batch.py` - Batch processing with AI
- `ai/parallel_extractor.py` - Parallel extraction coordinator
- `ai/prompts.py` - Prompt templates for structuring
- `ai/conversation.py` - Conversation management
- `ai/tracker.py` - Progress tracking

**Processing Tools:**
- `processing/process_batch.py` - Batch page processing
- `processing/fix_processing_status.py` - Fix processing status tracking

### Phase 3: Rule Extraction

**Extraction Scripts:**
- `extract_all_remaining.py` - Extract all remaining rules from OCR
- `batch_extract_rules.py` - Batch rule extraction
- `batch_extract_remaining_rules.py` - Extract remaining rules
- `extraction/extract_rules.py` - Core rule extraction logic
- `extraction/extract_one_rule.py` - Extract single rule
- `extraction/extract_cli_new.py` - CLI for interactive extraction

**Rule-Specific Extractors:**
- `extract_rules_501_600.py` - Extract rules §501-600
- `extract_rules_701_800.py` - Extract rules §701-800

**Analysis and Search:**
- `deep_search_missing_rules.py` - Find missing rules in OCR
- `deep_audit_rules.py` - Audit rule completeness
- `analyze_stub_rules.py` - Identify stub rules
- `check_stub_rules.py` - Check for incomplete rules

**Appendix Extraction:**
- `extract_appendix.py` - Extract appendix from OCR
- `create_appendix.py` - Create structured appendix sections

### Phase 3 → Phase 4 Transformation

**Schema Conversion:**
- `convert_all_old_schema.py` - Convert all old schema to new format
- `convert_old_schema.py` - Single file schema converter

**Content Cleanup:**
- `add_sanskrit_tags.py` - Add @deva[] @[] tags to Sanskrit terms
- `fix_alphabet_tagging.py` - Fix alphabet section tagging
- `fix_all_footnotes.py` - Fix footnote associations
- `fix_footnotes_39_45.py` - Fix specific footnote range
- `fix_footnotes_correct.py` - Correct footnote placement
- `fix_rule_formatting.py` - Standardize rule formatting
- `restore_rule_headers.py` - Restore § headers

**Phase 4 Production:**
- `phase4_create_unified_images.py` - Create unified image directory
- `phase4_update_rule_files.py` - Update image paths in rules

### Utilities

**Page and Image Processing:**
- `utilities/extract_and_ocr_missing_pages.py` - OCR missing pages
- `utilities/find_missing_pages_in_pdf.py` - Identify missing pages
- `utilities/identify_missing_pages.py` - Page gap analysis
- `utilities/ocr_missing_pages.py` - Process missing pages
- `utilities/ocr_correct_pages.py` - Re-OCR specific pages
- `utilities/structure_missing_ocr_files.py` - Organize missing OCR

**Rule Processing:**
- `utilities/reprocess_rules.py` - Re-extract specific rules
- `utilities/scan_pdf_for_missing_rules.py` - Find rules in PDF

**Validation:**
- `validate_all_rules.py` - Validate all rule files
- `analysis/review_results.py` - Review extraction results

### Support Scripts

**Infrastructure:**
- `load_env.py` - Environment variable loader
- `serve_images.py` - Local image server for testing
- `build_page_mapping.py` - Build page mapping between sources

**Deprecated/One-off:**
- `batch_manual_ocr.py` - Manual OCR intervention
- `batch_ocr_251_260.py` - Process specific page range
- `multi_source_ocr.py` - Multi-source reconciliation

## Usage Examples

### Extract All Remaining Rules

```bash
python3 scripts/extract_all_remaining.py
```

Searches OCR sources for all missing rules and extracts them automatically.

### Convert Schema Format

```bash
python3 scripts/convert_all_old_schema.py
```

Converts all rules from old schema format to new standardized format.

### Add Sanskrit Tagging

```bash
python3 scripts/add_sanskrit_tags.py
```

Adds proper @deva[] and @[] tags to Sanskrit terms throughout rules.

### Validate Rules

```bash
python3 scripts/validate_all_rules.py
```

Validates all rule files have proper schema and content.

### Create Phase 4 Images

```bash
python3 scripts/phase4_create_unified_images.py
```

Creates unified image directory for production with consistent paths.

## Script Organization

### ai/ - AI-Assisted Extraction
Claude-powered extraction pipeline with conversation management, parallel processing, and prompt templates.

### extraction/ - Rule Extraction Tools
Core extraction logic, CLI interfaces, and interactive extraction tools.

### processing/ - Batch Processing
Batch processing coordinators and status management.

### utilities/ - Helper Scripts
One-off utilities for specific tasks like finding missing pages, re-processing rules, etc.

### analysis/ - Analysis Tools
Scripts for reviewing results, auditing completeness, and quality checks.

## Notes

- Most scripts were created for specific one-off tasks during the pipeline
- Many are now obsolete after Phase 4 completion
- Core scripts (extract_all_remaining.py, convert_all_old_schema.py) remain useful
- Scripts use environment variables from .env file (see .env.template)
- AI scripts require ANTHROPIC_API_KEY
- OCR scripts require GOOGLE_APPLICATION_CREDENTIALS and ANTHROPIC_API_KEY

## Environment Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install google-cloud-vision anthropic pdf2image pillow python-dotenv pyyaml

# Copy and configure .env
cp .env.template .env
# Edit .env with your API keys
```

## Dependencies

- `google-cloud-vision` - Google Vision OCR
- `anthropic` - Claude AI API
- `pdf2image` - PDF to image conversion
- `pillow` - Image processing
- `python-dotenv` - Environment variables
- `pyyaml` - YAML parsing
