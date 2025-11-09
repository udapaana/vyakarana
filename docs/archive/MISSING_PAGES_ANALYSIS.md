# Missing Pages Analysis

## Summary

**158 out of 972 rules are missing** from `structured_pages/` directory. The OCR was completed for all 729 PDF pages, but many pages were not converted to structured markdown files.

## Root Cause

1. **Phase 1 (OCR)**: ✅ Completed - All 729 pages OCR'd with Google + Claude
2. **Phase 2 (Structuring)**: ❌ Incomplete - Only 814 rules out of 972 were structured
   - Some OCR outputs were never converted to structured markdown
   - Page numbering mismatches caused confusion
   
## Specific Example: § 7-10

### Current State
- `structured_pages/page_013.md` → § 5-6
- `structured_pages/page_014.md` → § 11-12 ← Jump! Missing § 7-10

### Where They Are
- **PDF Page 24** (PyPDF2 index 23): Contains § 7-8
- **PDF Page 25** (PyPDF2 index 24): Contains § 9-10
- **OCR Output**: These pages exist in `ocr_output/google/` and `ocr_output/claude/` but weren't structured

### Page Numbering Confusion
- PDF page numbers (1-732) 
- Book page numbers in headers (1-729)
- OCR output filenames (page_001 - page_729)
- Structured page filenames (page_001 - page_729, but with gaps)

**The offset**: OCR `page_N` ≈ PDF page `N+9` in early sections

## All Missing Rules

Total: 158 rules missing

Missing rule ranges:
- § 7-10 (4 rules)
- § 32-33 (2 rules)  
- § 81, 93, 121 (3 rules)
- § 167-168, 172-175, 185-186 (9 rules)
- ... and 140 more

See `missing_rules.txt` for complete list.

## Fix Required

### Option A: Re-run Phase 2 Structuring on ALL OCR output
```bash
# Process all OCR outputs into structured pages
python3 scripts/structure_all_ocr.py
```

### Option B: Find and structure only missing pages
```bash
# Identify which OCR files correspond to missing rules
python3 find_missing_ocr_files.py

# Structure only those files
python3 structure_missing_pages.py
```

### Option C: Extract missing PDF pages and re-OCR
```bash
# Extract PDF pages 24-25 and ~156 others
python3 extract_missing_pdf_pages.py

# Run OCR on them
python3 scripts/batch_ocr.py source/missing_pages/*.png

# Structure the results
python3 structure_new_pages.py
```

## Recommendation

**Option B** is most efficient:
1. The raw OCR already exists in `ocr_output/`
2. We just need to identify which files weren't structured
3. Run the structuring pipeline on those specific files
4. Insert into `structured_pages/` with correct numbering

## Next Steps

1. ✅ Identified the problem (158 missing rules)
2. ✅ Found root cause (structuring phase incomplete)
3. ⏳ Map OCR files to missing rules
4. ⏳ Structure the missing OCR outputs
5. ⏳ Insert into structured_pages/
6. ⏳ Re-run rule extraction on complete source

## Files Created

- `missing_rules.txt` - List of all 158 missing rule numbers
- `missing_pages_found.txt` - PDF pages containing missing rules
- This document - Analysis and action plan
