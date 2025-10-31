# OCR Processing Pipeline Overview

**Project**: Kale's Higher Sanskrit Grammar (1894) - Digital Edition
**Goal**: Convert scanned PDF to structured, searchable, parseable markdown

---

## Complete Pipeline: 4 Phases

```
┌─────────────┐
│   Phase 1   │  Raw OCR Extraction
│     OCR     │  PDF → Raw Text (Claude + Google)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Phase 2   │  Reconciliation & Structuring  ◄── WE ARE HERE
│  STRUCTURE  │  Raw Text → Structured Markdown
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Phase 3   │  Rule Assembly
│  ASSEMBLE   │  Page Fragments → Complete Rules
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Phase 4   │  Enhancement & Validation
│   ENHANCE   │  Quality Pass + Sanskrit Completion
└──────┬──────┘
       │
       ▼
    Final Output
```

---

## Phase 1: Raw OCR Extraction ✅ COMPLETE

### Purpose

Extract text from scanned PDF pages using two OCR engines for redundancy and quality.

### Input

- Source: `source/*.pdf` (scanned pages of the 1894 grammar book)
- Format: PDF images, ~800 pages total

### Process

1. **Claude OCR**: Extract text using Claude's vision capabilities
   - Good at: Devanagari script, maintaining layout
   - Produces: High-quality text with structure awareness

2. **Google Vision OCR**: Extract text using Google Cloud Vision API
   - Good at: Overall accuracy, handling degraded scans
   - Produces: Reliable baseline text

### Output

```
ocr_output/
├── claude/
│   ├── page_001.txt    # Raw text extracted by Claude
│   ├── page_001.json   # Metadata
│   └── page_001.png    # Page image
└── google/
    ├── page_001.txt    # Raw text extracted by Google
    └── page_001.png    # Page image
```

### Status

✅ **COMPLETE**

- 726 pages with both Claude and Google OCR
- Quality: High (both engines performed well)
- Issues: Some character misreads (expected), handled in Phase 2

### Scripts

- OCR extraction scripts (not in current repo - completed separately)

---

## Phase 2: Reconciliation & Structuring ◄── CURRENT PHASE

### Purpose

Reconcile differences between OCR outputs, fix errors, and structure into semantic markdown with YAML front matter.

### Input

- `ocr_output/claude/page_NNN.txt`
- `ocr_output/google/page_NNN.txt`
- Style guide: `docs/STRUCTURING_RAW_OCR.md`

### Process (3 Stages per page)

**Stage 2.1: Reconciliation**

- Compare Claude vs Google OCR character-by-character
- Where they agree: use that text
- Where they differ: use better reading (Claude for Devanagari, context for Latin)
- Fix obvious OCR errors (spacing, character misreads: 0/o, 1/l, rn/m)
- Output: Clean reconciled raw text

**Stage 2.2: Structuring**

- Add YAML front matter with metadata (rule numbers, topics, citations, etc.)
- Tag all Sanskrit terms:
  - Devanagari: `@deva[देवनागरी]`
  - IAST: `@[devanāgarī]`
- Convert emphasis markers: `**Obs.**` → `@note[type=observation]:`
- Standardize footnotes: `*` → `[^1]:`
- Convert headers: `**§ 20.**` → `## § 20.`
- Extract metadata (cross-refs, examples, terms)

**Stage 2.3: Validation**

- Verify content preservation (target: 95%+ match with original)
- Track OCR corrections made
- Flag pages needing review
- Output: Validation report

### Output

```
structured_pages/
├── page_001.md               # Structured markdown with YAML front matter
├── page_001_validation.json  # Validation report
├── page_002.md
└── ...

data/
├── processing_status.json    # Which pages processed, needs review
└── consistency_data.json     # Cross-page consistency tracking
```

### Status

⚙️ **IN PROGRESS**

- 36 pages processed (test run)
- Issues identified and prompt improved
- Ready to reprocess all 726 pages with fixes

### Scripts

- `scripts/processing/process_batch.py` - Main processor
- `scripts/analysis/review_results.py` - Quality review

### Current Issues & Fixes

See: `docs/ISSUES_FOUND.md` and `docs/FIXES_APPLIED.md`

---

## Phase 3: Rule Assembly & Linking (FUTURE)

### Phase 3.1: Extract Table of Contents & Build Link Graph

### Purpose

Create a comprehensive TOC and establish bidirectional links between all references in the text.

### Input

- `structured_pages/page_NNN.md` (all pages)
- YAML front matter: `rule`, `cross_refs`, `panini_refs`

### Process

**3.1.1: Extract Structure**

- Parse all pages to identify:
  - Rule numbers (§ 1, § 2, ... § N)
  - Chapter boundaries
  - Section hierarchies
  - Subsection markers (a, b, c, ...)
- Build hierarchical structure of entire grammar

**3.1.2: Build Reference Graph**

- Map all cross-references:
  - `"See § 18"` → link to rule_018.md
  - `cross_refs: [{rule: §20}]` → bidirectional link
  - `panini_refs: ["Pāṇ. VI. 1. 89"]` → external reference
- Create reverse index: "Rule § 18 is cited by: § 15, § 22, § 45"

**3.1.3: Generate Markdown Links**

- Convert references to clickable markdown links:

  ```markdown
  # Before

  See § 18 for details on sandhi.

  # After

  See [§ 18](rule_018.md) for details on sandhi.
  ```

- Add backlinks section to each rule:
  ```markdown
  ## Referenced By

  - [§ 15](rule_015.md) - Prerequisites
  - [§ 22](rule_022.md) - Applications
  ```

**3.1.4: Create Table of Contents**

- Generate hierarchical TOC with links:

  ```markdown
  # Table of Contents

  ## Part I: Sandhi

  ### Chapter 1: Vowel Sandhi

  - [§ 18. Introduction to Sandhi](rule_018.md)
  - [§ 19. Similar Vowels](rule_019.md)
  - [§ 20. Guṇa Substitution](rule_020.md)

  ### Chapter 2: Consonant Sandhi

  - [§ 31. Nasal Changes](rule_031.md)
    ...
  ```

### Output

```
metadata/
├── toc.md                       # Main table of contents with links
├── toc.json                     # Structured TOC data
├── link_graph.json              # Complete reference graph
├── reverse_index.json           # "Cited by" mappings
└── external_references.json     # Pāṇini refs, other citations

structured_pages/                # Updated with links
├── page_001.md                 # Now has markdown links to referenced rules
└── ...
```

### Link Types Handled

**Internal Rule References**:

- Direct: `§ 18`, `§§ 15-20`
- In text: "See § 18 for details"
- In YAML: `cross_refs: [{rule: §18}]`
- Contextual: "as shown above in § 15"

**Pāṇini References** (External):

- Format: `Pāṇ. VI. 1. 89`
- Could link to: Online Ashtadhyayi resources
- Or: Note as external reference

**Cross-References**:

- Prerequisites: "Before studying this, see § 11"
- Continuations: "This rule is continued in § 21"
- See also: "Compare with § 45"
- Exceptions: "Except as noted in § 67"

### Benefits

- **Navigation**: Click to jump between related rules
- **Context**: See what cites each rule (reverse links)
- **Discovery**: TOC shows complete structure
- **Validation**: Ensure all references are valid
- **Frontend**: Ready for web/app with working hyperlinks

### Status

📅 **PLANNED**

- Will run after Phase 2 completes
- Estimated time: ~3-5 hours processing
- Automated with validation pass

### Scripts (To Be Created)

- `scripts/linking/extract_toc.py`
- `scripts/linking/build_link_graph.py`
- `scripts/linking/add_markdown_links.py`
- `scripts/linking/generate_toc.py`
- `scripts/linking/validate_links.py`

---

### Phase 3.2: Assemble Complete Rules

### Purpose

Merge page fragments into complete rule files.

### Input

- `structured_pages/page_NNN.md` (with links from 3.1)
- Metadata: `continues_from`, `continues_to`, `rule` fields
- Link graph from Phase 3.1

### Process

1. **Identify rule boundaries**
   - Some rules span multiple pages
   - Use `rule: § N` metadata to group pages
   - Track `continues_from` / `continues_to` relationships

2. **Merge page fragments**
   - Combine pages belonging to same rule
   - Example: Rule § 20 (pages 19-20) → `rules/rule_020.md`
   - Preserve all metadata, merge word indices, combine content
   - Maintain internal links

3. **Add navigation**

   ```markdown
   ---

   # At top of rule file

   ← [Previous: § 19](rule_019.md) | [Next: § 21](rule_021.md) →
   [Table of Contents](../toc.md)

   # At bottom

   ## See Also

   - [§ 18 - Sandhi Introduction](rule_018.md)
   - [§ 45 - Related exceptions](rule_045.md)

   ## Referenced By

   - [§ 22 - Applications](rule_022.md)
   - [§ 35 - Counter-exceptions](rule_035.md)
   ```

### Output

```
rules/
├── rule_001.md          # Complete Rule § 1 with links
├── rule_020.md          # Complete Rule § 20 (merged from pages 19-20)
├── rule_021.md          # Complete Rule § 21
└── ...

navigation/
├── prev_next.json       # Sequential navigation
└── related_rules.json   # Semantic relationships
```

### Status

📅 **PLANNED**

- Will begin after Phase 3.1 completes
- Estimated time: ~5-7 hours processing
- Mostly automated with manual review

### Scripts (To Be Created)

- `scripts/assembly/assemble_rules.py`
- `scripts/assembly/add_navigation.py`
- `scripts/assembly/validate_completeness.py`

---

## Phase 4: Enhancement & Validation (FUTURE)

### Purpose

Final quality pass to catch remaining issues and enhance metadata.

### Input

- `structured_pages/page_NNN.md` and/or `rules/rule_NNN.md`
- `consistency_data.json`

### Process

**Stage 4.1: Sanskrit Term Enhancement**

- Identify remaining untagged Sanskrit (get from 95% → 99%+)
- Add proper IAST with diacritics for any missed terms
- Ensure consistency across all files

**Stage 4.2: Metadata Completion**

- Fill empty `panini_refs` fields where applicable
- Add missing `citations` arrays
- Complete cross-references between rules
- Build comprehensive term glossary

**Stage 4.3: Final Validation**

- Run consistency checks across entire corpus
- Validate YAML syntax in all files
- Check Sanskrit tagging coverage (target: 99%+)
- Generate quality report

**Stage 4.4: Index Generation**

- Build complete word index (all Devanagari words)
- Create term glossary (all technical terms)
- Generate citation index
- Create cross-reference graph

### Output

```
enhanced_pages/         # OR update structured_pages/ in place
├── page_001.md        # Fully enhanced
└── ...

final/
├── complete_grammar.md           # Optional: single compiled file
├── word_index.json              # All Devanagari words
├── term_glossary.json           # All technical terms
├── citation_index.json          # All references
└── cross_reference_graph.json   # Rule relationships
```

### Status

📅 **PLANNED**

- Lighter work thanks to Phase 2 fixes
- Estimated time: ~10-15 hours processing
- Semi-automated with manual review

### Scripts (To Be Created)

- `scripts/enhancement/enhance_sanskrit.py`
- `scripts/enhancement/complete_metadata.py`
- `scripts/validation/validate_corpus.py`
- `scripts/indexing/build_indices.py`

---

## Data Flow Diagram

```
┌─────────────┐
│  source/    │
│  *.pdf      │  Original scanned PDFs
└──────┬──────┘
       │
       │ Phase 1: OCR (DONE)
       ▼
┌─────────────────────────┐
│  ocr_output/            │
│  ├── claude/page_*.txt  │  Raw OCR text
│  └── google/page_*.txt  │  (Two sources)
└───────────┬─────────────┘
            │
            │ Phase 2: Structure (IN PROGRESS)
            ▼
┌───────────────────────────────┐
│  structured_pages/            │
│  ├── page_*.md                │  Structured markdown
│  └── page_*_validation.json  │  + YAML front matter
└─────────────┬─────────────────┘
              │
              │ Phase 3: Assemble (PLANNED)
              ▼
┌───────────────────┐
│  rules/           │
│  └── rule_*.md    │  Complete rules
└─────────┬─────────┘
          │
          │ Phase 4: Enhance (PLANNED)
          ▼
┌─────────────────────┐
│  final/             │
│  ├── *.md           │  Enhanced output
│  └── indices/*.json │  + Comprehensive indices
└─────────────────────┘
```

---

## Time Estimates

| Phase              | Status         | Estimated Time   | Actual Time |
| ------------------ | -------------- | ---------------- | ----------- |
| Phase 1: OCR       | ✅ Complete    | ~10 hours        | ~12 hours   |
| Phase 2: Structure | ⚙️ In Progress | ~30-35 hours     | TBD         |
| Phase 3: Assemble  | 📅 Planned     | ~5-10 hours      | -           |
| Phase 4: Enhance   | 📅 Planned     | ~10-15 hours     | -           |
| **Total**          |                | **~55-70 hours** | **TBD**     |

_Processing can run in background, batches of 10 pages_

---

## Key Decisions

### Why Two OCR Engines?

- **Redundancy**: Catch errors missed by one engine
- **Quality**: Compare outputs to choose best reading
- **Devanagari**: Claude excels at Indic scripts
- **Accuracy**: Google provides reliable baseline

### Why 3 Stages in Phase 2?

- **Reconcile**: Merge best of both OCR outputs
- **Structure**: Add semantic markup and metadata
- **Validate**: Ensure no content loss, track quality

### Why Separate Phase 3 (Assembly)?

- **Page-based processing** in Phase 2 keeps files manageable
- **Rule-based access** in Phase 3 better for end users
- **Both structures** serve different purposes

### Why Phase 4 Enhancement?

- **Impossible to be 100% perfect** in automated processing
- **Final pass** catches edge cases and rare patterns
- **Human review** for quality assurance
- **Comprehensive indices** add significant value

---

## Current Status Summary

**✅ Phase 1**: Complete - 726 pages OCR'd
**⚙️ Phase 2**: In progress - 36 pages done, prompt fixed, ready to reprocess all
**📅 Phase 3**: Planned - will start after Phase 2
**📅 Phase 4**: Planned - will start after Phase 3

**Next Action**: Reprocess all 726 pages in Phase 2 with improved prompt

---

## Related Documentation

- **Style Guide**: `docs/STRUCTURING_RAW_OCR.md` - Formatting rules for Phase 2
- **Issues Found**: `docs/ISSUES_FOUND.md` - Problems identified in test run
- **Fixes Applied**: `docs/FIXES_APPLIED.md` - How issues are resolved
- **Directory Structure**: `docs/DIRECTORY_STRUCTURE.md` - File organization
- **Comprehensive Review**: `docs/COMPREHENSIVE_REVIEW.md` - Quality analysis

---

**Last Updated**: 2025-10-26
**Version**: 1.0
