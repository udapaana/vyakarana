# API Safety - Scripts Disabled

**Date:** 2024-10-31
**Action:** All API-calling scripts have been disabled to prevent accidental costs

## Disabled Scripts

### OCR Scripts (Phase 1)
All Phase 1 OCR scripts have been disabled since OCR is already complete (729 pages processed).

- `scripts/claude_vision_ocr.py.disabled` - Claude Vision API OCR
- `scripts/google_vision_ocr.py.disabled` - Google Vision API OCR
- `scripts/google_vision_ocr_simple.py.disabled` - Simplified Google Vision
- `scripts/dual_ocr.py.disabled` - Main dual OCR orchestrator
- `scripts/batch_ocr.py.disabled` - Batch processing

**Status:** Phase 1 complete (729 pages, 590MB output). No need to re-run.

### Extraction Scripts (Phase 3)
API-based extraction scripts disabled. Use CLI-based scripts instead.

- `scripts/extraction/extract_rules_llm.py.disabled` - Anthropic API extraction
- `scripts/extraction/extract_rules_llm_local.py.disabled` - Anthropic API extraction (local variant)

**Alternative:** Use `extract_cli_new.py` or `extract_rules_subprocess.py` which call `claude` CLI instead.

## Active (Safe) Scripts

### CLI-Based Extraction
✅ **These scripts are SAFE** - they use the `claude` CLI wrapper, not direct API calls:

- `scripts/extraction/extract_cli_new.py` - Compact CLI-based extraction
- `scripts/extraction/extract_rules_subprocess.py` - Verbose CLI-based extraction

### Utility Scripts
✅ **These scripts don't make API calls:**

- `scripts/load_env.py` - Environment variable checker (no API calls)
- `scripts/preprocess_image.py` - Image preprocessing only
- `scripts/compare_quality.py` - Source quality comparison
- `scripts/download_7th_edition_sources.py` - Download sources
- `scripts/verify_7th_edition.py` - Verify edition
- `scripts/extraction/extract_rules.py` - Regex-based extraction (deprecated, but no API)
- `scripts/extraction/extract_one_rule.py` - Utility helper
- `scripts/extraction/extract_rules_interactive.py` - Task generator

## Re-enabling Scripts

If you need to re-enable any script (NOT recommended):

```bash
# Don't do this unless you really need to and understand the costs
mv scripts/claude_vision_ocr.py.disabled scripts/claude_vision_ocr.py
```

## Cost Summary

**Phase 1 (COMPLETE - DO NOT RE-RUN):**
- Google Vision: ~$1.09 for 729 pages
- Claude Vision: ~$12-15 for 729 pages
- **Total spent: ~$13.85**

**Phase 3 (CLI-based - No additional API costs):**
- Uses local `claude` CLI wrapper
- No per-call charges
- Safe to run

## Recommended: Use CLI Scripts Only

For Phase 3 rule extraction, use:

```bash
# Test first
python3 scripts/extraction/extract_cli_new.py --start 1 --end 10 --output rules_test

# Full extraction
python3 scripts/extraction/extract_cli_new.py --start 1 --end 972 --output rules
```

This uses your local Claude Code instance instead of API calls.
