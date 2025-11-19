# Phase 2 Execution Guide

## Overview

**Goal:** Clean all 731 OCR pages by removing headers/footers and adding YAML frontmatter.

**Status:** 10/731 pages complete (pages 001-007, 009-010, 012)

**Approach:** AI cleans each page individually (not scriptable due to OCR inconsistency)

## Quick Start

### 1. Check Current Status

```bash
python3 scripts/validate_phase2_mapping.py
```

This runs 5 validation checks and shows:
- Source coverage (all 731 pages accounted for)
- Internal page sequence (no gaps)
- Rule sequence (§1 to §972)
- Output filename convention
- Corrected mapping with image paths

### 2. Plan Next Batch

```bash
python3 scripts/clean_pages_batch.py 11 20
```

Shows what pages 11-20 will include:
- Output filename (page_011.md)
- Source file (page_011.txt from claude or official_1931)
- Internal page number (book's actual page)
- Content type (§N or preface/contents/etc)
- Image path for reference

### 3. Clean Pages

For each page in the batch:

1. **Get source info from mapping:**
   ```bash
   jq '.[] | select(.output_page == 11)' phase2_corrected_mapping.json
   ```

2. **Read source file:**
   ```bash
   cat phase1_ocr/claude/page_011.txt
   ```

3. **View source image (if needed):**
   ```bash
   open phase1_ocr/claude/page_011.png
   ```

4. **Clean the page** using AI following [PHASE2_AI_CLEANING_GUIDE.md](./PHASE2_AI_CLEANING_GUIDE.md)

5. **Save to phase2_cleaned/**
   ```bash
   # Output file: phase2_cleaned/page_011.md
   ```

### 4. Validate

After cleaning a batch:
```bash
python3 scripts/validate_phase2_mapping.py
```

Should show no errors, and your newly cleaned pages in CHECK 4 output.

## Key Files

| File | Purpose |
|------|---------|
| **phase2_corrected_mapping.json** | Authoritative source→output mapping (731 pages) |
| **phase1_ocr/claude/** | Complete OCR source (731 pages, some errors) |
| **phase1_ocr/sources/official_1931/** | Better quality OCR (713 pages, missing § 2, § 3) |
| **phase1_ocr/images/** | Source page images for reference |
| **phase2_cleaned/** | Output directory (target: 731 .md files) |
| **scripts/validate_phase2_mapping.py** | Validation framework |
| **scripts/clean_pages_batch.py** | Batch planning helper |

## Mapping Structure

Each entry in `phase2_corrected_mapping.json`:

```json
{
  "output_page": 13,
  "output_file": "page_013.md",
  "source_file": "page_013.txt",
  "source_path": "phase1_ocr/claude/page_013.txt",
  "source_type": "claude",
  "source_image": "phase1_ocr/claude/page_013.png",
  "image_exists": true,
  "internal_page": 5,
  "rules": [5, 6],
  "content_type": "§5"
}
```

**Key fields:**
- `output_page`: Sequential 1-731
- `output_file`: Where to save cleaned page
- `source_path`: Where to read raw OCR
- `source_image`: Reference image path
- `internal_page`: Book's actual page number (i, ii, 1, 2, 3...)
- `rules`: Rule numbers found on this page
- `content_type`: Quick description

## Page Variants

Some pages split into variants (e.g., page_013.txt, page_013a.txt, page_013b.txt). These are:
- Sorted by internal page number (not alphabetically)
- Mapped to sequential output pages
- Example:
  - page_013.txt (internal 5) → page_013.md
  - page_013a.txt (internal 6) → page_014.md
  - page_013b.txt (internal 7) → page_015.md

## Cleaning Guidelines

See [PHASE2_AI_CLEANING_GUIDE.md](./PHASE2_AI_CLEANING_GUIDE.md) for detailed instructions on:
- What to remove (headers, footers)
- What to keep (rules, content, tables)
- How to handle footnotes
- YAML frontmatter format
- Examples

### YAML Frontmatter Format

```yaml
---
page_number: 13        # Sequential output page (1-731)
internal_page: 5       # Book's actual page (i, ii, 1, 2, 3...)
chapter: "The Alphabet"
section: "alphabet"
rules_starting: ["§ 5", "§ 6"]  # Rules that BEGIN on this page
rules_continuing: []             # Rules continuing from previous page
has_footnotes: false
---
```

## Validation Framework

The validation script performs 5 checks:

### Check 1: Source Coverage
- Discovers all source files
- Groups page variants
- Reports total files found

### Check 2: Internal Page Sequence
- Extracts internal page numbers from headers
- Checks for gaps in sequence
- Shows first 30 pages with their internal numbers

### Check 3: Rule Number Sequence
- Extracts all § N patterns
- Checks for large gaps in rule numbering
- Reports rule range (§1 to §972)

### Check 4: Output Filename Convention
- Reads YAML frontmatter from cleaned files
- Verifies filename matches page_number
- Shows internal_page for each cleaned file

### Check 5: Corrected Mapping
- Creates authoritative source→output mapping
- Sorts by internal page number (handles variants correctly)
- Adds image path tracking
- Saves to phase2_corrected_mapping.json
- Shows first 20 mapped pages with image status

## Common Issues

### Issue: "Image missing for page_NNN"
- **Cause:** Source image doesn't exist
- **Fix:** Check if alternate source (claude vs official_1931) has the image
- **Rare:** All 731 current pages have images

### Issue: "INTERNAL PAGE GAP: Page N is missing"
- **Cause:** No source file contains internal page N
- **Fix:** Search other sources (official_1931, google) for missing page
- **Status:** No gaps found in current mapping (1-731)

### Issue: "filename page_NNN != page_number:NNN"
- **Cause:** YAML frontmatter page_number doesn't match filename
- **Fix:** Correct the YAML frontmatter
- **Prevention:** Use mapping to get correct page_number

## Dual Source Strategy

We have two OCR sources:

**claude** (731 pages, complete)
- ✅ Complete coverage, no gaps
- ✅ Has § 2, § 3 (missing from official_1931)
- ⚠️ Some OCR errors (§ → 3)

**official_1931** (713 pages, gaps)
- ✅ Better quality OCR
- ✅ Fewer OCR errors
- ⚠️ Missing 18 pages including § 2, § 3

**Current approach:** Using claude as primary source since it has complete coverage. Can reference official_1931 for quality comparison when claude has obvious errors.

## Progress Tracking

Track your progress:

```bash
# Count cleaned pages
ls phase2_cleaned/page_*.md | wc -l

# List remaining pages
python3 -c "
import json
with open('phase2_corrected_mapping.json') as f:
    mapping = json.load(f)

cleaned = set(int(f.split('_')[1].split('.')[0])
              for f in $(ls phase2_cleaned/page_*.md))

remaining = [e['output_page'] for e in mapping
             if e['output_page'] not in cleaned]

print(f'Cleaned: {len(cleaned)}/731')
print(f'Remaining: {len(remaining)}')
print(f'Next 10: {remaining[:10]}')
"
```

## After Phase 2

Once all 731 pages are cleaned:

### Phase 2b: Concatenate Pages
```bash
# Create master document
cat phase2_cleaned/page_*.md > phase2_master.md
```

### Phase 3: Extract Rules
- Extract § N to § N+1 from master document
- Natural overlap ensures no content lost
- Target: 972 individual rule files
- See [RULE_EXTRACTION_SCHEMA.md](./RULE_EXTRACTION_SCHEMA.md)

### Phase 4: Production
- Validate schema compliance
- Build cross-references
- Create navigation indices
- See [PHASE4_README.md](./PHASE4_README.md)

## Estimated Time

- **Per page:** ~30-60 seconds (read, clean, save)
- **Per batch (10 pages):** ~10 minutes
- **Total (721 remaining):** ~72 batches × 10 min = ~12 hours
- **Parallelizable:** Can clean multiple pages simultaneously

## Questions?

See related documentation:
- [PHASE2_AI_CLEANING_GUIDE.md](./PHASE2_AI_CLEANING_GUIDE.md) - Detailed cleaning instructions
- [PHASE2_VALIDATION_RULES.md](./PHASE2_VALIDATION_RULES.md) - Validation framework details
- [RULE_EXTRACTION_SCHEMA.md](./RULE_EXTRACTION_SCHEMA.md) - Target schema for Phase 3
