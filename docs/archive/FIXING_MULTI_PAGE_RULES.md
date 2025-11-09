# Fixing Multi-Page Rule Extraction

## Problem Statement

Rules that span multiple pages can be incomplete if the extraction process doesn't properly detect and merge content across page boundaries.

### Example: Rule § 3
- **Page 11 ends**: "udātta is"
- **Page 12 starts**: "that which proceeds from..."
- **Issue**: Extraction stopped at page 11, cutting off mid-sentence

## Root Cause

The pipeline has three phases:
1. **Phase 1 (OCR)**: Extracts text from each PDF page independently ✅ Works correctly
2. **Phase 2 (Structuring)**: Adds YAML metadata including `continues_to` markers ⚠️ Marks but doesn't merge
3. **Phase 3 (Rule Extraction)**: Reads structured pages and extracts rules ❌ May miss continuations

The issue is in **Phase 3**: The extraction logic needs to:
- Detect when a rule continues beyond current page
- Read subsequent pages until the rule is complete
- Update metadata (page_end, source_pages) correctly

## Solutions Implemented

### 1. Enhanced Prompt (✅ Completed)

Updated `scripts/ai/parallel_extractor.py` with:

```python
full_prompt = f"""Extract rule § {rule_num} from the following pages.

CRITICAL INSTRUCTIONS:
1. Find where § {rule_num} starts

2. Extract ALL content for § {rule_num} including:
   - Complete explanation (DO NOT CUT OFF mid-sentence)
   - All subsections (a), (b), (c), etc.
   - All footnotes [^1], [^2], etc.
   - Everything until the NEXT rule § {rule_num + 1} starts

3. DETECT CONTINUATION: If the rule text is cut off at the bottom of a page:
   - Check if "continues_from" or "continues_to" in YAML
   - Look for incomplete sentences at page boundaries
   - Read content from next page until rule § {rule_num} is COMPLETE

4. Determine ACTUAL end page where § {rule_num} finishes

5. Output format:
   Line 1: {{"end_page": N, "source_pages": ["page_XXX.md", "page_YYY.md"]}}
   Rest: Complete markdown with YAML front matter

EXAMPLE of continuation detection:
  Page 11 ends: "udātta is"
  Page 12 starts: "that which proceeds from..."
  → This is CONTINUATION - include both pages!
"""
```

### 2. Response Parsing (✅ Completed)

Updated to extract `source_pages` from Claude's response:

```python
# Parse {"end_page": N, "source_pages": [...]} from first line
for i, line in enumerate(lines[:5]):
    json_match = re.search(r'\{[^}]+\}', line)
    if json_match:
        try:
            metadata = json.loads(json_match.group(0))
            end_page = metadata.get("end_page", start_page + 1)
            source_pages = metadata.get("source_pages", [])
            content_start = i + 1
            break
        except:
            pass
```

### 3. Schema Validation (✅ Completed)

Validates that extracted rules have:
- Correct `page_end` (not just page_start)
- Complete `source_pages` array
- All required YAML fields

## Automated Detection

Created `check_incomplete_rules.py` to detect potentially incomplete rules:

```bash
python3 check_incomplete_rules.py
```

**Detection Criteria:**
1. `page_start == page_end` but `continues_to` exists in source
2. Only 1 `source_page` but continuation marker exists
3. Content ends with incomplete sentence patterns:
   - Ends with "is", "are", "the", "and", "or", "of", "to"
   - Pattern: `\bis\s*\[?\^?\d*\]?\s*$`

## Manual Fixes Applied

### Rule § 3 (✅ Fixed)
- **Before**: page_end: 11, source_pages: ["page_011.md"]
- **After**: page_end: 12, source_pages: ["page_011.md", "page_012.md"]
- **Content**: Added continuation from page 012

### Rule § 2 (✅ No fix needed)
- False positive from checker
- Actually complete despite `continues_to` marker in source
- The continuation is between rules, not within the rule

## Prevention Strategy

### Short Term: Validation & Reprocessing

1. **Run validation after extraction**:
```bash
python3 check_incomplete_rules.py
```

2. **Reprocess incomplete rules**:
```bash
python3 scripts/utilities/reprocess_rules.py --rule 3
```

### Long Term: Pipeline Improvements

#### Option A: Fix at Phase 2 (Recommended for next version)

Enhance Phase 2 structuring to merge continued rules:

```python
# When structuring, if continues_to exists:
# - Read next page
# - Merge content until rule boundary
# - Create single structured page with complete rule
```

**Pros**: Phase 3 works with complete content
**Cons**: Requires restructuring existing phase2_structured/ files

#### Option B: Fix at Phase 3 (Current approach)

Keep Phase 2 as-is, make Phase 3 smarter:

1. ✅ Read multiple pages (currently reads 10)
2. ✅ Detect continuation markers in YAML
3. ✅ Check for incomplete sentences
4. ✅ Prompt Claude to extract complete content
5. ⚠️ **Limitation**: Requires Claude CLI for extraction

**Pros**: No Phase 2 changes needed
**Cons**: Depends on Claude correctly following instructions

#### Option C: Post-Processing Validator

Add a Phase 3.5 validation step:

```python
# After extraction:
# 1. Check each rule for completeness
# 2. If incomplete, re-extract with explicit continuation
# 3. Update rule file
# 4. Log corrections
```

**Pros**: Catches errors after they occur
**Cons**: Extra processing step, requires reprocessing

## Current Status

- **Total rules**: 972
- **Extracted**: 41
- **With continuations**: 105 rules total
- **Incomplete**: 1 (rule § 3, now fixed)
- **False positives**: 1 (rule § 2)

## Recommendations

1. **Immediate**: Continue Phase 3 extraction with enhanced prompt
2. **Monitor**: Run `check_incomplete_rules.py` after each batch
3. **Fix**: Use `reprocess_rules.py` for any incomplete rules found
4. **Future**: Consider Phase 2 enhancement to merge continuations at structure time

## Testing

To test the fix on a specific rule:

```bash
# Check current state
grep -A 3 "page_end:" phase3_rules/rule_003.md
grep "source_pages:" phase3_rules/rule_003.md

# Validate completeness
python3 check_incomplete_rules.py | grep "rule_003"

# Reprocess if needed
python3 scripts/utilities/reprocess_rules.py --rule 3
```

## Files Modified

- `scripts/ai/parallel_extractor.py` - Enhanced prompt & parsing
- `phase3_rules/rule_003.md` - Manual fix applied
- `check_incomplete_rules.py` - Validation script (new)
- `docs/FIXING_MULTI_PAGE_RULES.md` - This document (new)
