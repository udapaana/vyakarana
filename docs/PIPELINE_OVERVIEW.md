# OCR Processing Pipeline Overview

**Project**: Kale's Higher Sanskrit Grammar (1894) - Digital Edition
**Goal**: Convert scanned PDF to structured, searchable markdown with all 972 grammar rules

---

## Complete Pipeline: 3 Phases

```
┌─────────────┐
│   Phase 1   │  Multi-Source OCR Extraction
│     OCR     │  PDF → Raw Text (Multiple Sources + Engines)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Phase 2+3    │  Direct Rule Extraction ◄── WE ARE HERE
│  EXTRACT    │  OCR → Individual Rule Files
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Phase 4   │  Enhancement & Validation
│   ENHANCE   │  Quality Pass + Linking + Indices
└──────┬──────┘
       │
       ▼
    Final Output
```

---

## Phase 1: Multi-Source OCR ✅ COMPLETE

### Purpose
Extract text from scanned PDFs using multiple sources and OCR engines for maximum accuracy.

### Multi-Source Strategy

**Three PDF Sources**:
1. **DLI Google** (Digital Library of India via Google) - 729 pages
   - Primary source, good overall quality
   - OCR: Google Vision + Claude Vision
2. **DLI Claude** (DLI processed by Claude) - 729 pages
   - Same source, Claude-enhanced
   - OCR: Claude Vision
3. **Official_1931** (Official 7th Edition scan) - 732 pages
   - Alternative scan with some unique pages
   - OCR: Claude Vision

**Complementary OCR Engines**:
- **Google Cloud Vision** - Excellent Devanagari script recognition (धी, भू, सू)
- **Claude Vision** - Superior IAST diacriticals (ā, ī, ū, ṛ, ṃ, ḥ, ṭ, ḍ, ṇ, ś, ṣ)

### Output

```
phase1_ocr/
├── google/              # DLI Google source + Google Vision OCR
│   ├── page_001.txt
│   ├── page_001.json
│   └── page_001.png
├── claude/              # DLI Claude source + Claude Vision OCR
│   ├── page_001.txt
│   └── ...
└── official_1931/       # Official source + Claude Vision OCR
    ├── page_001.txt
    └── ...
```

### Status

✅ **COMPLETE**
- All 3 sources fully OCR'd
- ~729 pages per source (official has 732)
- Ready for Phase 2+3 extraction

---

## Phase 2+3: Direct Rule Extraction ⚙️ IN PROGRESS

**Key Decision**: Merged Phase 2 (structuring) and Phase 3 (assembly) into single-step extraction.

### Why Merge Phase 2+3?

Original plan had two steps:
1. Phase 2: OCR → `structured_pages/page_NNN.md` (page-based)
2. Phase 3: Pages → `rules/rule_NNN.md` (rule-based)

**Problem**: Rules span multiple pages, creating complex assembly logic.

**Solution**: Extract rules directly from multi-source OCR using dynamic sliding window approach.

### Dynamic Sliding Window Method

See: `docs/DYNAMIC_SLIDING_WINDOW.md` for full methodology.

**Concept**:
- Process 15-page windows of OCR from all sources
- AI detects last complete rule in window
- Next window starts at next rule
- Extracts complete rules regardless of page boundaries

**Benefits**:
- Rules extracted as complete units (not split across files)
- Multi-source reconciliation happens during extraction
- No intermediate `structured_pages/` needed
- Simpler pipeline with better results

### Process

**For each rule extraction**:

1. **Gather multi-source OCR** for current window
   ```
   Window: pages 12-26
   - phase1_ocr/google/page_012.txt ... page_026.txt
   - phase1_ocr/claude/page_012.txt ... page_026.txt
   - phase1_ocr/official_1931/page_020.txt ... page_034.txt (offset mapping)
   ```

2. **AI extraction with cross-verification**
   - Compare all available OCR sources
   - Select best readings (Google for Devanagari, Claude for IAST)
   - Extract complete rule with YAML metadata
   - Follow RULE_EXTRACTION_SCHEMA.md format

3. **Generate structured rule file**
   ```markdown
   ---
   rule: § 7
   page: 13
   source_pages:
     dli: [13]
     official_1931: [21]
   chapter: The Alphabet
   topics: [consonants, aspiration]
   word_index:
     - अल्पप्राण
     - महाप्राण
   ---

   ## § 7. Aspiration of Consonants

   Some consonants are pronounced with slight aspiration...
   ```

### Output

```
phase3_rules/
├── rule_001.md          # Complete Rule § 1
├── rule_002.md          # Complete Rule § 2
├── ...
└── rule_972.md          # Complete Rule § 972

data/
└── phase3_extraction_status.json    # Tracking extraction progress
```

### Status

⚙️ **IN PROGRESS**
- **963 rules extracted** (99.1% coverage)
  - 37 fully enhanced with all metadata
  - 926 stub files with basic structure
- **Missing**: 9 rules (pages not in any OCR source)
- **Next**: Enhance remaining 926 stubs with full content

### Format Specification

All rules follow: `docs/RULE_EXTRACTION_SCHEMA.md`

**Key standards**:
- YAML frontmatter with complete metadata
- Content includes `## § N. Title` header
- Sanskrit tagged as `@deva[देवनागरी]` and `@[IAST]`
- Visarga in IAST uses `ḥ` not `:`
- Cross-references, Pāṇini citations preserved
- Tables in markdown format

---

## Phase 4: Enhancement & Validation 📅 PLANNED

### Purpose
Final quality pass, linking, and comprehensive indexing.

### Process

**4.1: Complete Stub Enhancement**
- Fill in 926 stub files with full OCR content
- Apply multi-source reconciliation
- Ensure all metadata fields populated

**4.2: Link Building**
- Link Pāṇini references to local GRETIL Ashtadhyayi
- Link Pāṇini references to online ashtadhyayi.com
- Build cross-reference graph between rules
- Add navigation (previous/next, see also)

**4.3: Index Generation**
- Complete word index (all Sanskrit terms)
- Term glossary (technical definitions)
- Citation index (all Pāṇini references)
- Topic taxonomy

**4.4: Table of Contents**
- Generate hierarchical TOC markdown file
- Extract from rule titles and YAML metadata
- Link to individual rules and appendices
- Include Pāṇini references

**4.5: Final Validation**
- Validate all YAML syntax
- Check Sanskrit tagging coverage (target 99%+)
- Verify all links resolve
- Generate quality report

### Output

```
phase3_rules/            # Updated with full content
├── rule_001.md         # Fully enhanced
└── ...

metadata/
├── toc.md              # Hierarchical table of contents
├── word_index.json     # Complete word index
├── term_glossary.json  # Technical terms
├── citation_index.json # Pāṇini references
└── cross_refs.json     # Rule relationships

references/
└── ashtadhyayi/        # Local Pāṇini sūtra files from GRETIL
    └── ...
```

### Status

📅 **PLANNED**
- Will begin after stub enhancement completes
- Estimated: ~15-20 hours processing
- Semi-automated with validation

---

## Data Flow Diagram

```
┌──────────────┐
│  source/     │
│  *.pdf       │  Original scanned PDFs (3 sources)
└──────┬───────┘
       │
       │ Phase 1: Multi-Source OCR ✅
       ▼
┌──────────────────────┐
│  phase1_ocr/         │
│  ├── google/         │  Raw OCR text
│  ├── claude/         │  (Multiple sources
│  └── official_1931/  │   + engines)
└──────────┬───────────┘
           │
           │ Phase 2+3: Direct Extraction ⚙️
           ▼
┌──────────────────────┐
│  phase3_rules/       │
│  └── rule_*.md       │  Complete rules with YAML
└──────────┬───────────┘
           │
           │ Phase 4: Enhancement 📅
           ▼
┌──────────────────────┐
│  metadata/           │
│  references/         │  Final output + indices
│  phase3_rules/       │  + linking
└──────────────────────┘
```

---

## Current Status Summary

| Phase | Status | Progress | Notes |
|-------|--------|----------|-------|
| **Phase 1** | ✅ Complete | 100% | All 3 sources OCR'd |
| **Phase 2+3** | ⚙️ In Progress | 99.1% | 963/972 rules extracted |
| **Phase 4** | 📅 Planned | 0% | Awaiting stub enhancement |

**Next Actions**:
1. Enhance 926 stub files with full OCR content
2. Build Pāṇini reference links (local GRETIL + online)
3. Generate table of contents from rule metadata
4. Create comprehensive indices

---

## Key Decisions

### Why Multi-Source OCR?
- **Complementary strengths**: Google→Devanagari, Claude→IAST
- **Cross-validation**: Compare multiple scans of same page
- **Error reduction**: Agreement across sources confirms accuracy
- **99%+ coverage**: Different scans have different page numbers/suffixes

### Why Merge Phase 2+3?
- **Rules span pages**: Extracting by page creates assembly complexity
- **Better results**: AI can extract complete rules as semantic units
- **Simpler pipeline**: Fewer steps, less chance of errors
- **Multi-source reconciliation**: Happens during extraction, not after

### Why Dynamic Sliding Window?
- **Complete rules**: AI detects rule boundaries, extracts full content
- **Efficient**: Only process pages needed for current rules
- **Resumable**: Track progress, resume from last rule
- **Flexible**: Works with variable-length rules (1 page to 5+ pages)

---

## Related Documentation

- **Official Spec**: `docs/RULE_EXTRACTION_SCHEMA.md` - Output format
- **Extraction Method**: `docs/DYNAMIC_SLIDING_WINDOW.md` - How we extract
- **Phase 1 Details**: `docs/phase1/PHASE1_OCR.md` - OCR methodology
- **Folder Structure**: `docs/FOLDER_STRUCTURE.md` - Directory organization
- **Sources**: `docs/SOURCES.md` - Source PDF information

---

**Last Updated**: 2025-11-08
**Version**: 2.0 (Merged Phase 2+3)
