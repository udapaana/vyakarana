# Phase 1: Dual OCR Extraction

## Overview

Phase 1 extracts raw text from the source PDF using two complementary OCR engines to maximize accuracy for Sanskrit mixed-script content.

## Status: ✅ Complete

- **Pages processed**: 728/729 (page 2 intentionally blank)
- **Total cost**: ~$14 USD
- **Duration**: ~5-6 hours for full run
- **Output**: `ocr_output/claude/` and `ocr_output/google/`

## OCR Engines

### Google Cloud Vision API
- **Strengths**: Excellent Devanagari recognition, batch processing
- **Cost**: $1.50 per 1,000 images = ~$1.09 for 729 pages
- **Language hints**: Sanskrit, English
- **Output**: Text with confidence scores

### Claude Vision (Anthropic)
- **Strengths**: Superior IAST diacritics, mixed scripts, layout understanding
- **Cost**: ~$12-15 for 729 pages (varies by response length)
- **Prompt**: Custom character-by-character transcription prompt
- **Output**: Text with token usage metadata

## Image Preprocessing Pipeline

Each page undergoes preprocessing before OCR:

1. **Deskewing** - Correct rotated/skewed pages
2. **Border removal** - Remove scanning artifacts
3. **Noise reduction** - Median filter (kernel size 2)
4. **Contrast enhancement** - 1.3x boost
5. **Sharpness enhancement** - 1.2x boost

**Implementation**: `scripts/preprocess_image.py`

## Scripts

### Main OCR Scripts

- **`dual_ocr.py`** - Main orchestrator for dual OCR
  - Runs both engines on each page
  - Saves preprocessed images and OCR results
  - Usage: `python3 scripts/dual_ocr.py --pdf <path> --start 1 --end 729`

- **`batch_ocr.py`** - Single-engine batch processor (Google only)
  - Usage: `python3 scripts/batch_ocr.py --start 1 --end 100`

- **`claude_vision_ocr.py`** - Claude Vision module
  - Function: `ocr_pdf_page(pdf_path, page_num, output_dir)`
  - Returns: `{text, usage, timestamp}`

- **`google_vision_ocr_simple.py`** - Google Vision module
  - Function: `ocr_pdf_page(pdf_path, page_num, output_dir, api_key)`
  - Returns: `{text, confidence, timestamp}`

- **`preprocess_image.py`** - Image preprocessing utilities
  - Functions: `deskew_image()`, `remove_borders()`, `preprocess_for_ocr()`

### Utility Scripts

- **`compare_quality.py`** - Compare multiple source PDFs
- **`download_7th_edition_sources.py`** - Download source candidates
- **`verify_7th_edition.py`** - Verify edition metadata

## Output Format

Each page produces three files per engine:

```
ocr_output/
  google/
    page_001.txt     # Plain text transcription
    page_001.json    # Full response: {text, confidence, timestamp}
    page_001.png     # Preprocessed image
  claude/
    page_001.txt     # Plain text transcription
    page_001.json    # Full response: {text, usage: {input/output tokens}, timestamp}
    page_001.png     # Preprocessed image (same as Google)
```

## Running Phase 1

### Prerequisites

```bash
# Install dependencies
pip install google-cloud-vision anthropic pdf2image pillow python-dotenv

# Set up API keys in .env
GOOGLE_CLOUD_VISION_API_KEY=AIza...
ANTHROPIC_API_KEY=sk-ant-...
```

### Full Batch Run

```bash
# Process all pages with both engines
python3 scripts/dual_ocr.py \
  --pdf source/candidates/DLI_2015_IGNCA_Delhi.pdf \
  --start 1 \
  --end 729 \
  --google-output ocr_output/google \
  --claude-output ocr_output/claude
```

### Process Specific Pages

```bash
# Single page
python3 scripts/dual_ocr.py --pdf <path> --pages 44

# Page range
python3 scripts/dual_ocr.py --pdf <path> --start 100 --end 150
```

### Rerunning Phase 1

Phase 1 is **fully rerunnable**:

1. **Full rerun**: Delete `ocr_output/` directory and rerun scripts
2. **Partial rerun**: Delete specific page files and rerun with `--pages` or `--start/--end`
3. **Single engine**: Use `batch_ocr.py` for Google only, or modify `dual_ocr.py`

The scripts check for existing files and skip them by default (can override).

## Performance

- **Time per page**: 20-28 seconds (both engines)
- **Full run**: ~5-6 hours for 729 pages
- **Parallelization**: Can run multiple instances with different page ranges
- **Cost**: ~$0.019 per page (both engines)

## Quality Results

- **Average confidence**: 87%+ (Google Vision metric)
- **Devanagari accuracy**: >95% with Google
- **IAST diacritics**: >90% with Claude
- **Mixed script**: Claude handles better than Google
- **Tables/layout**: Claude preserves structure better

## No MCP Server Needed

Phase 1 uses standard API calls:
- Google Cloud Vision REST API
- Anthropic Claude API via official Python SDK

No MCP (Model Context Protocol) server is needed for Phase 1.

## Troubleshooting

### Missing poppler

Error: `Unable to get page count. Is poppler installed and in PATH?`

**Solution**: Install poppler-utils
```bash
# macOS
brew install poppler

# Ubuntu/Debian
apt-get install poppler-utils
```

### API Rate Limits

- **Google**: 1,800 requests/min (plenty for this use case)
- **Claude**: Varies by tier; use delays if hitting limits

### Missing Pages

If pages are missing OCR output:
1. Check `ocr_output/google/` and `ocr_output/claude/` for .txt files
2. Rerun with specific page numbers: `--pages 101,397,448`
3. Check error logs in console output

## Next Phase

Output from Phase 1 feeds into Phase 2 (OCR Reconciliation), which:
- Compares Google and Claude OCR character-by-character
- Selects best reading from each engine
- Structures into markdown with YAML metadata
- Tags Sanskrit terms with proper IAST

See [PHASE2_STATUS.md](PHASE2_STATUS.md) for Phase 2 documentation.
