# Documentation Index

This directory contains all project documentation organized by topic.

## Project Overview
- [Main README](../README.md) - Project overview and getting started
- [Table of Contents](TABLE_OF_CONTENTS.md) - Comprehensive table of contents for the grammar

## Phase Documentation

### Phase 1: OCR (Complete)
- OCR output stored in `ocr_output/claude/` and `ocr_output/google/`
- 731 pages processed with dual OCR (Google Vision + Claude Vision)

### Phase 2: Structuring (Complete)
- [Phase 2 Completion Report](PHASE_2_COMPLETION_REPORT.md)
- All 972 rules structured in `structured_pages/`
- Includes newly added pages 013a, 013b (§ 7-10)
- [Missing Pages Analysis](MISSING_PAGES_ANALYSIS.md) - Historical documentation of gap fixes

### Phase 3: Extraction (In Progress)
- [Phase 3 Summary](PHASE_3_SUMMARY.md)
- [Parallel Extraction Guide](PARALLEL_EXTRACTION.md)
- Current status: 72/972 rules extracted (7.4%)

## Planning & Strategy
- [Extraction Plan](EXTRACTION_PLAN.md)
- [Quick Start Guide](QUICK_START.md)
- [Simple Extraction](SIMPLE_EXTRACTION.md)
- [Extraction with Browser Auth](EXTRACTION_WITH_BROWSER_AUTH.md)
- [Ready for Extraction](READY_FOR_EXTRACTION.md)

## Technical Documentation
- [API Safety](API_SAFETY.md)
- [Claude AI Wrapper Summary](CLAUDE_AI_WRAPPER_SUMMARY.md)
- [README Extraction](README_EXTRACTION.md)

## Directory Structure

```
/
├── docs/                      # All documentation (you are here)
├── scripts/                   # All scripts and utilities
│   ├── ai/                   # AI-powered extraction scripts
│   ├── extraction/           # Extraction-related scripts
│   ├── utilities/            # Utility scripts for maintenance
│   └── ...
├── structured_pages/         # Phase 2 output: 731 structured pages
├── rules/                    # Phase 3 output: Extracted individual rules
├── ocr_output/              # Phase 1 output: Raw OCR results
│   ├── claude/              # Claude Vision OCR
│   └── google/              # Google Vision OCR
└── source/                  # Source PDF files
```

## Key Files in Root
- `parallel_extract.sh` - Main extraction runner
- `validate_all_rules.py` - Validation script
- `README.md` - Main project documentation
