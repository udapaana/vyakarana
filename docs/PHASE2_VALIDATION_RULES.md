# Phase 2 Validation Rules

## Overview
These checks ensure Phase 2 cleaned pages maintain structural integrity and completeness.

## Validation Checks

### Check 1: Source Coverage
**Purpose:** Discover all source page variants (page_013a.txt, page_013b.txt, etc.)

**Rules:**
- Scan all `phase1_ocr/claude/page_*.txt` files
- Group by base page number (e.g., 013, 013a, 013b)
- Report any pages with variants (these need special handling)

**Expected:** ~731+ files (including variants like 013a, 013b)

---

### Check 2: Internal Page Sequence
**Purpose:** Ensure internal page numbers are sequential without gaps

**Rules:**
- Extract internal page number from each source file header
  - Pattern 1: `"N    SANSKRIT GRAMMAR"`  
  - Pattern 2: `"§ N-M ]   CHAPTER   . N"`
  - Special: Preface (roman i, ii, iii), Contents (v, vi), Abbreviations (viii)
- Sort by internal page number
- Check for gaps in sequence

**Expected:** Sequential internal pages (i, ii, iii... 1, 2, 3, 4...)

**Gaps allowed:**
- Roman to Arabic transition (iii -> 1) is OK
- No gaps within Arabic numbers (1, 2, 3, 4, 5...)

---

### Check 3: Rule Number Sequence
**Purpose:** Verify grammar rules (§ N) are mostly sequential

**Rules:**
- Extract all `§ N.` patterns from source files
- Handle OCR corruption: `3 N.` at line start = `§ N.`
- Sort rules numerically
- Flag large gaps (>10 rules) as warnings

**Expected:** §1 through §972 with minimal gaps

**Known exceptions:**
- § 2, § 3 missing from official_1931 source (use claude)
- Appendix rules may have gaps

---

### Check 4: Output Filename Convention
**Purpose:** Ensure output files follow naming convention

**Rules:**
- Output filename: `page_NNN.md` where NNN = sequential output number (001, 002...)
- YAML frontmatter must have:
  ```yaml
  page_number: NNN          # Must match filename
  internal_page: M          # Internal page from source
  ```
- `page_number` in YAML must match filename number

**Example:**
```
phase2_cleaned/page_013.md
---
page_number: 13             # Matches filename ✓
internal_page: 5            # From source page_013.txt (§5-6)
```

---

### Check 5: Source-to-Output Mapping
**Purpose:** Create correct mapping accounting for page variants

**Rules:**
- Process source pages in sorted order:
  - page_013.txt (base)
  - page_013a.txt (variant a)
  - page_013b.txt (variant b)
- Each source file maps to ONE output file sequentially
- Output page increments for each source (including variants)

**Example mapping:**
```
page_012.md <- page_012.txt     (internal p.4,  §4)
page_013.md <- page_013.txt     (internal p.5,  §5-6)
page_014.md <- page_013a.txt    (internal p.6,  §7-8)
page_015.md <- page_013b.txt    (internal p.7,  §9-10)  
page_016.md <- page_014.txt     (internal p.8,  §11-12)
```

**Key insight:** 
- Output page number (filename) = sequential scan order
- Internal page number (YAML) = actual book page
- These are DIFFERENT!

---

## Gap Handling Strategy

### When gaps are found in source:

1. **Check if it's a real gap:**
   - Look for page variants (013a, 013b)
   - Check both claude and official_1931 sources
   - Verify against original scanned images

2. **If gap is real (missing pages):**
   - Document in mapping JSON: `"missing": true`
   - Create placeholder output file noting gap
   - Continue with next available page

3. **If gap is from page variants:**
   - Include ALL variants in sequential output
   - Maintain internal page sequence in YAML

---

## Dual-Source Integration

### When both claude and official_1931 available:

1. **Match by content, not by filename:**
   - Find pages with same § rules in both sources
   - official_1931 has confusing naming (front_017.txt = internal p.17)
   - claude is sequential (page_009.txt usually has § 1)

2. **Quality preference:**
   - **Primary:** official_1931 (better diacritics, cleaner Sanskrit)
   - **Fallback:** claude (complete coverage, may have OCR errors)
   - **Best:** Show both to AI for comparison

3. **Missing rules handling:**
   - § 2, § 3 only in claude (missing from official_1931)
   - Use claude source for these
   - Document in mapping: `"source": "claude_only"`

---

## Running Validation

```bash
# Run all checks
python3 scripts/validate_phase2_mapping.py

# Creates:
# - phase2_corrected_mapping.json (use this for cleaning)
# - Validation report with errors/warnings

# If validation fails:
# 1. Review errors in output
# 2. Check source files manually
# 3. Update mapping as needed
# 4. Re-run validation
```

---

## Success Criteria

✅ All checks pass without errors
✅ Warning count acceptable (<5% of pages)
✅ Corrected mapping covers all source files
✅ No gaps in internal page sequence (except known transitions)
✅ All 972 grammar rules accounted for

---

## Next Steps After Validation

1. Use `phase2_corrected_mapping.json` for Phase 2 cleaning
2. Process each source file to output file per mapping
3. Run validation again on cleaned output
4. Verify concatenation produces continuous text
