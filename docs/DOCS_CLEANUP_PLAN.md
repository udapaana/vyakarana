# Documentation Cleanup Plan

## Current Reality vs. Docs

### What We Actually Have:
- **Phase 1**: Multi-source OCR (DLI Google, DLI Claude, Official_1931 Claude) ✅ Complete
- **Phase 2+3 MERGED**: Direct extraction from OCR to phase3_rules/ using DYNAMIC_SLIDING_WINDOW.md ✅ In Progress
  - 963 rules extracted (99.1% coverage)
  - No intermediate structured_pages/ directory
- **Official Spec**: RULE_EXTRACTION_SCHEMA.md

### What Docs Describe (WRONG):
- Phase 2: Create structured_pages/ (never happened)
- Phase 3: Assemble rules from structured_pages/ (we skip this)
- Phase 4: Enhancement (not started)
- MARKDOWN_SPEC.md conflicts with RULE_EXTRACTION_SCHEMA.md

---

## Files to DELETE

### Obsolete/Conflicting Specs
- [ ] `docs/MARKDOWN_SPEC.md` ❌ Conflicts with RULE_EXTRACTION_SCHEMA.md

### Obsolete Phase 2 Docs (we merged Phase 2+3)
- [ ] `docs/PHASE_2_COMPLETION_REPORT.md` ❌ Never happened this way
- [ ] `docs/PHASE2_STATUS.md` ❌ Obsolete approach
- [ ] `docs/PHASE2_STREAM_APPROACH.md` ❌ Obsolete approach
- [ ] `docs/PHASE2_V2_PLAN.md` ❌ Never implemented
- [ ] `docs/STRUCTURING_RAW_OCR.md` ❌ Obsolete (structured_pages/ unused)

### Obsolete Extraction Docs
- [ ] `docs/EXTRACTION_PLAN.md` ❌ Check if superseded by DYNAMIC_SLIDING_WINDOW.md
- [ ] `docs/EXTRACTION_WITH_BROWSER_AUTH.md` ❌ Check relevance
- [ ] `docs/PARALLEL_EXTRACTION.md` ❌ Check if superseded
- [ ] `docs/PARALLEL_PROCESSING_STRATEGY.md` ❌ Check if superseded
- [ ] `docs/SIMPLE_EXTRACTION.md` ❌ Check if superseded
- [ ] `docs/PHASE_3_AI_WRAPPER.md` ❌ Check if superseded
- [ ] `docs/PHASE_3_SUMMARY.md` ❌ Check if outdated
- [ ] `docs/READY_FOR_EXTRACTION.md` ❌ Check if obsolete

### Duplicate/Redundant Docs
- [ ] `docs/FOLDER_STRUCTURE.md` vs `docs/DIRECTORY_STRUCTURE.md` - Keep one
- [ ] `docs/README.md` vs root `README.md` vs `START_HERE.md` - Consolidate

### Status/Tracking Docs (may be outdated)
- [ ] `docs/PROGRESS.md` ❌ Likely outdated
- [ ] `docs/PHASE3_STATUS_TRACKING.md` ❌ We have data/phase3_extraction_status.json
- [ ] `docs/PHASE3_EXTRACTION_VALIDATION.md` ❌ Check if relevant
- [ ] `docs/COMPREHENSIVE_REVIEW.md` ❌ Likely outdated
- [ ] `docs/MISSING_PAGES_ANALYSIS.md` ❌ Check if still relevant

### Error/Fix Docs (archive or delete)
- [ ] `docs/ALL_EXTRACTION_ERRORS_AND_FIXES.md` ❌ Archive
- [ ] `docs/FIXING_MULTI_PAGE_RULES.md` ❌ Archive
- [ ] `docs/ROOT_CAUSE_CONTINUATION_ISSUE.md` ❌ Archive

---

## Files to KEEP (Essential)

### Core Specs & Standards
- ✅ `docs/RULE_EXTRACTION_SCHEMA.md` - **OFFICIAL SPEC**
- ✅ `docs/CODING_STANDARDS.md` - Code quality
- ✅ `docs/API_SAFETY.md` - Security guidelines

### Current Approach
- ✅ `docs/DYNAMIC_SLIDING_WINDOW.md` - **CURRENT EXTRACTION METHOD**
- ✅ `docs/PHASE1_MULTI_SOURCE.md` - Multi-source OCR approach
- ✅ `docs/PHASE1_OCR.md` - Phase 1 methodology

### Reference & Setup
- ✅ `docs/SOURCES.md` - Source material info
- ✅ `docs/SETUP_API_KEYS.md` - API configuration
- ✅ `docs/QUICK_START.md` - Getting started (UPDATE)
- ✅ `docs/TABLE_OF_CONTENTS.md` - Phase 3 TOC plan

### Summaries (if accurate)
- ✅ `docs/CLAUDE_AI_WRAPPER_SUMMARY.md` - Check if current
- ✅ `docs/README_EXTRACTION.md` - Check if current

---

## Files to UPDATE

### Main Entry Points
- [ ] `README.md` - Update to reflect merged Phase 2+3 pipeline
- [ ] `START_HERE.md` - Update current status and next steps
- [ ] `NEXT_STEPS_PHASE2.md` - Rename to NEXT_STEPS.md, update for current phase

### Pipeline Documentation
- [ ] `docs/PIPELINE_OVERVIEW.md` - **MAJOR UPDATE NEEDED**
  - Remove Phase 2 as separate step
  - Document merged Phase 2+3 direct extraction
  - Update status to reflect 963 rules extracted
  - Point to DYNAMIC_SLIDING_WINDOW.md for methodology

### Directory Structure
- [ ] `docs/DIRECTORY_STRUCTURE.md` - Update to show phase3_rules/, remove structured_pages/

### Quick Start
- [ ] `docs/QUICK_START.md` - Update for current workflow

---

## Recommended New Structure

```
docs/
├── RULE_EXTRACTION_SCHEMA.md        # Official spec (KEEP)
├── DYNAMIC_SLIDING_WINDOW.md        # Current method (KEEP)
├── CODING_STANDARDS.md              # Code quality (KEEP)
├── API_SAFETY.md                    # Security (KEEP)
├── PIPELINE_OVERVIEW.md             # UPDATE - current pipeline
├── DIRECTORY_STRUCTURE.md           # UPDATE - actual structure
├── QUICK_START.md                   # UPDATE - current workflow
├── TABLE_OF_CONTENTS.md             # Phase 3 TOC planning (KEEP)
├── SOURCES.md                       # Source PDFs (KEEP)
├── SETUP_API_KEYS.md                # API setup (KEEP)
├── phase1/                          # Phase 1 docs
│   ├── PHASE1_OCR.md
│   └── PHASE1_MULTI_SOURCE.md
└── archive/                         # Historical/reference docs
    ├── PHASE2_*.md                  # Old Phase 2 approaches
    ├── EXTRACTION_*.md              # Old extraction attempts
    └── *_ERRORS_AND_FIXES.md        # Historical fixes
```

---

## Execution Order

1. **Delete MARKDOWN_SPEC.md** (conflicts with official spec)
2. **Archive obsolete Phase 2 docs** (never used this approach)
3. **Update PIPELINE_OVERVIEW.md** (reflect merged Phase 2+3)
4. **Update README.md and START_HERE.md** (current status)
5. **Clean up remaining obsolete docs**
6. **Organize into subdirectories** (phase1/, archive/)

---

## Action Items

- [ ] Review and confirm deletion list
- [ ] Create docs/archive/ for historical docs
- [ ] Create docs/phase1/ for Phase 1 specific docs
- [ ] Delete MARKDOWN_SPEC.md immediately
- [ ] Update PIPELINE_OVERVIEW.md with current reality
- [ ] Update README.md with current status
- [ ] Clean up root-level .md files (consolidate guides)
