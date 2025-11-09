# Phase 2 v2: Multi-Source Reconciliation - Implementation Plan

**Last Updated**: 2025-11-07
**Status**: 📋 **PLANNED**

---

## Overview

Phase 2 v1 successfully reconciled dual OCR engines (Google + Claude) on a single PDF source (DLI_2015), achieving 99%+ accuracy. Phase 2 v2 will expand to reconcile **multiple PDF sources + multiple OCR engines** for maximum accuracy.

---

## Motivation

### Why Multiple PDF Sources?

Different scans of the same book have varying quality:
- **Page-level variations**: Page 44 might be clearer in DLI_2015, while page 45 is clearer in Official_1931
- **Scan artifacts**: Different scans have different artifacts (blur, contrast, skew)
- **OCR performance**: OCR accuracy varies based on source image quality
- **Redundancy**: Multiple scans provide validation and error detection

### Current Limitations

Phase 2 v1 uses only DLI_2015 source:
- Misses opportunities to use better quality pages from other sources
- No validation against other scans
- Some pages may have poor quality in DLI_2015 but good quality in other sources

---

## Available Sources

| Source | Pages | OCR Engines | Status | Notes |
|--------|-------|-------------|--------|-------|
| **DLI_2015** | 729 | Google + Claude | ✅ Complete | Primary source, best overall quality |
| **Official_1931** | 732 | Claude | ⚙️ Partial | OCR'd version, 3 extra pages |
| **xMqc_1931** | 729 | Claude | 📋 Planned | Alternative scan, needs OCR |

---

## Implementation Strategy

### Step 1: Complete OCR Processing

**For Official_1931**:
```bash
# Check current status
ls phase1_ocr/images/official_1931/ | wc -l

# Process remaining pages with Claude Vision
python3 scripts/claude_vision_ocr.py \
  --source official_1931 \
  --start-page 1 \
  --end-page 732 \
  --output phase1_ocr/sources/official_1931/
```

**For xMqc_1931**:
```bash
# Extract images from PDF
python3 scripts/extract_source_images.py \
  --source xmqc_1931 \
  --start 1 --end 729

# Process with Claude Vision
python3 scripts/claude_vision_ocr.py \
  --source xmqc_1931 \
  --start-page 1 \
  --end-page 729 \
  --output phase1_ocr/sources/xmqc_1931/
```

### Step 2: Build Page Equivalency Mapping

Create `config/page_equivalency.json` mapping logical pages across sources:

```json
{
  "1": {
    "dli_2015": 1,
    "official_1931": 1,
    "xmqc_1931": 1
  },
  "2": {
    "dli_2015": 2,
    "official_1931": 2,
    "xmqc_1931": 2
  },
  "44": {
    "dli_2015": 44,
    "official_1931": 44,
    "xmqc_1931": 45
  },
  ...
  "729": {
    "dli_2015": 729,
    "official_1931": 732,
    "xmqc_1931": 729
  }
}
```

**Implementation**:
```bash
python3 scripts/build_page_equivalency.py \
  --sources dli_2015 official_1931 xmqc_1931 \
  --output config/page_equivalency.json \
  --interactive
```

Script should:
1. Display images from all sources side-by-side
2. Allow manual page number mapping
3. Auto-detect page numbers from OCR text
4. Save equivalency mapping

### Step 3: Implement Multi-Source Reconciliation

Update `scripts/processing/process_batch.py` to:

**3.1 Load All Available Sources**

For each logical page N:
```python
def get_all_ocr_for_page(logical_page: int) -> Dict[str, str]:
    """Get all OCR results for a logical page from all sources"""
    equivalency = load_page_equivalency()
    page_map = equivalency.get(str(logical_page), {})

    ocr_results = {}

    # DLI_2015 source
    if "dli_2015" in page_map:
        phys_page = page_map["dli_2015"]
        ocr_results["google_dli"] = read_ocr(f"phase1_ocr/google/page_{phys_page:03d}.txt")
        ocr_results["claude_dli"] = read_ocr(f"phase1_ocr/claude/page_{phys_page:03d}.txt")

    # Official_1931 source
    if "official_1931" in page_map:
        phys_page = page_map["official_1931"]
        ocr_results["claude_official"] = read_ocr(f"phase1_ocr/sources/official_1931/page_{phys_page:03d}.txt")

    # xMqc_1931 source
    if "xmqc_1931" in page_map:
        phys_page = page_map["xmqc_1931"]
        ocr_results["claude_xmqc"] = read_ocr(f"phase1_ocr/sources/xmqc_1931/page_{phys_page:03d}.txt")

    return ocr_results
```

**3.2 Update Reconciliation Prompt**

Modify Stage 1 (Reconciliation) prompt to handle N sources:

```python
prompt = f"""
You are reconciling {len(ocr_results)} OCR outputs of logical page {page_num}
from Kale's Higher Sanskrit Grammar (1894).

<style_guide>
{style_guide}
</style_guide>

<google_ocr_dli_2015>
{ocr_results.get("google_dli", "Not available")}
</google_ocr_dli_2015>

<claude_ocr_dli_2015>
{ocr_results.get("claude_dli", "Not available")}
</claude_ocr_dli_2015>

<claude_ocr_official_1931>
{ocr_results.get("claude_official", "Not available")}
</claude_ocr_official_1931>

<claude_ocr_xmqc_1931>
{ocr_results.get("claude_xmqc", "Not available")}
</claude_ocr_xmqc_1931>

TASK: Create a single reconciled version following these steps:

1. **Multi-source comparison**
   - Compare ALL available sources character-by-character
   - Where all sources agree: use that text with high confidence
   - Where sources differ:
     * For Devanagari: prefer Claude sources (better with Indic scripts)
     * For IAST diacriticals: prefer Claude sources
     * For general text: majority vote or best contextual reading
     * Consider image quality indicators if available
   - Track which sources were used for each section
   - **Fix obvious OCR errors**: spacing mistakes, character misreads (0/o, 1/l, rn/m)
   - For genuinely unclear text: mark with [?text?]

2. **Quality indicators**
   - High confidence: All sources agree
   - Medium confidence: Majority agree, or Claude sources agree
   - Low confidence: Sources disagree, chose most sensible reading
   - Mark uncertain sections for review

3. **Preserve original content**
   - Every word, number, symbol must appear in output (unless OCR artifact)
   - Fix OCR spacing/scanning errors
   - Keep author's spelling choices (even if archaic)
   - Keep all punctuation (unless clearly OCR error)
   - Do not modernize or "improve" the text

4. **Output format**
   - Raw text only (no markdown yet)
   - No commentary or explanations
   - Just the reconciled page content

Output the reconciled text now:
"""
```

**3.3 Track Source Usage**

Add metadata tracking which sources were used:

```yaml
---
rule: § 44
page: 44
sources_used:
  - source: dli_2015
    engines: [google, claude]
    physical_page: 44
    confidence: high
  - source: official_1931
    engines: [claude]
    physical_page: 44
    confidence: medium
  - source: xmqc_1931
    engines: [claude]
    physical_page: 45
    confidence: low
reconciliation_quality: high  # high/medium/low based on source agreement
---
```

### Step 4: Validation & Quality Control

**4.1 Source Agreement Analysis**

Create validation script to analyze source agreement:

```python
def analyze_source_agreement(structured_pages_dir: str):
    """Analyze how often sources agree"""

    agreement_stats = {
        "all_sources_agree": 0,
        "majority_agree": 0,
        "sources_disagree": 0,
        "single_source_only": 0
    }

    for page_file in structured_pages_dir.glob("page_*.md"):
        metadata = extract_yaml(page_file)
        quality = metadata.get("reconciliation_quality")

        if quality == "high":
            agreement_stats["all_sources_agree"] += 1
        elif quality == "medium":
            agreement_stats["majority_agree"] += 1
        elif quality == "low":
            agreement_stats["sources_disagree"] += 1

    return agreement_stats
```

**4.2 Comparison with Phase 2 v1**

Compare Phase 2 v2 output against Phase 2 v1 output:
- Identify pages with significant differences
- Flag for manual review if differences are substantial
- Track improvements and any regressions

```bash
python3 scripts/validation/compare_phase2_versions.py \
  --v1-dir structured_pages \
  --v2-dir structured_pages_v2 \
  --output validation/v1_v2_comparison.json
```

### Step 5: Reprocess All Pages

**5.1 Backup Phase 2 v1 Output**

```bash
mv structured_pages structured_pages_v1
mkdir structured_pages
```

**5.2 Run Multi-Source Processing**

```bash
python3 scripts/processing/process_batch_multisource.py \
  --start-page 1 \
  --end-page 729 \
  --equivalency config/page_equivalency.json \
  --output structured_pages \
  --batch-size 10
```

**5.3 Review & Manual Validation**

Focus review on:
- Pages where v1 and v2 differ significantly
- Pages marked as "low confidence" in reconciliation
- Pages where sources strongly disagreed
- Pages with unusual content or formatting

### Step 6: Update Phase 3 Dependencies

Phase 3 (rule extraction) depends on Phase 2 output:
- Verify Phase 3 scripts work with new metadata fields
- Rerun rule extraction if needed
- Update validation to ensure all 972 rules still present

---

## Benefits of Phase 2 v2

### Quantitative Improvements
- **More sources**: 3 PDF sources vs 1 → 3x redundancy
- **More OCR results**: Up to 4 OCR outputs per page vs 2 → 2x validation
- **Higher confidence**: Agreement across sources confirms accuracy
- **Better coverage**: Use best available source for each page

### Qualitative Improvements
- **Robustness**: Less dependent on single source quality
- **Error detection**: Easier to spot OCR errors when comparing multiple sources
- **Page-level optimization**: Use clearest scan for each individual page
- **Future-proof**: Framework supports adding more sources easily

---

## Timeline Estimate

| Task | Estimated Time | Dependencies |
|------|---------------|--------------|
| Complete Official_1931 OCR | 3-4 hours | None |
| Complete xMqc_1931 OCR | 3-4 hours | Image extraction |
| Build page equivalency | 2-3 hours | All OCR complete |
| Update reconciliation script | 3-4 hours | None (parallel) |
| Test multi-source reconciliation | 2 hours | Script + equivalency |
| Process all 729 pages | 15-20 hours | All above complete |
| Validation & review | 5-6 hours | Processing complete |
| **TOTAL** | **33-43 hours** | ~2-3 days processing time |

**Processing can run in background**: Actual hands-on time ~10-15 hours

---

## Success Criteria

Phase 2 v2 is successful if:

✅ **Coverage**: All 729 logical pages processed with multi-source reconciliation
✅ **Quality**: Average reconciliation quality ≥ Phase 2 v1 (99%+ accuracy)
✅ **Completeness**: All 972 rules still present and validated
✅ **Source usage**: ≥80% of pages use multiple sources for validation
✅ **Improvements**: Measurable improvements on pages where v1 had lower confidence
✅ **No regressions**: No pages with significantly worse quality than v1

---

## Rollback Plan

If Phase 2 v2 has issues:
1. Phase 2 v1 output backed up in `structured_pages_v1/`
2. Can restore immediately: `mv structured_pages_v1 structured_pages`
3. Phase 3 continues to work with v1 output
4. Investigate v2 issues offline without blocking progress

---

## Future Enhancements

After Phase 2 v2:
- **Confidence scoring**: ML-based confidence scores for reconciliation
- **Image quality metrics**: Automatically select best source based on image metrics
- **Interactive review**: Web UI for reviewing low-confidence pages
- **Additional sources**: Framework supports adding new PDF sources easily

---

## Related Documentation

- [PHASE2_STATUS.md](PHASE2_STATUS.md) - Phase 2 v1 completion report
- [PHASE2_COMPLETION_REPORT.md](PHASE_2_COMPLETION_REPORT.md) - v1 details
- [PIPELINE_OVERVIEW.md](PIPELINE_OVERVIEW.md) - Overall pipeline
- [README.md](../README.md) - Project overview with v2 strategy

---

**Ready to implement Phase 2 v2 multi-source reconciliation** 🚀
