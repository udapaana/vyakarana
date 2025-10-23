# Iterative Refinement Plan for Kale's Sanskrit Grammar

## Current Status

**Completed:**
- ✅ Initial OCR extraction (728 pages)
- ✅ Claude-based cleanup (728 chunks)
- ✅ Aggregation with structure normalization
- ✅ First standardization pass (v2 script)
  - Tagged common Sanskrit terms
  - Improved TOC formatting
  - Standardized section markers
  - Removed 412 redundant lines

**Current File:** `kales_sanskrit_grammar_standardized_v2.md`
- Size: 1.27 MB
- Lines: 18,733
- Format: Markdown with @[Sanskrit] tagging

## Remaining Issues to Address

### 1. Sanskrit Standardization (High Priority)

**Issues:**
- Inconsistent capitalization (some Sanskrit words in ALL CAPS)
- Missing @[...] tags for many Sanskrit terms
- Mix of tagged and untagged Sanskrit in same contexts
- Some pedagogical capitals that should remain (e.g., technical term first mentions)

**Strategy:**
1. Create comprehensive Sanskrit term dictionary
2. Tag all Sanskrit words consistently with @[...]
3. Convert all Sanskrit to proper IAST (ā, ī, ū, ṛ, etc.)
4. Preserve pedagogical capitals where needed (first mentions, emphasis)
5. Special handling for:
   - Devanagari script examples (keep as-is)
   - Grammatical formulas (e.g., @[अ + इ = ए])
   - Pāṇini sūtra references

**Tools Needed:**
- `sanskrit_standardizer.py` - comprehensive Sanskrit detection and tagging
- Dictionary of all Pāṇini terms, grammatical terms, example words

### 2. Broken Paragraphs and Flow (Medium Priority)

**Issues:**
- Some paragraphs still broken mid-sentence
- Inconsistent spacing around examples
- Lists not properly formatted as markdown lists

**Strategy:**
1. Identify truly broken paragraphs (no punctuation, continues thought)
2. Join intelligently based on:
   - Grammatical structure
   - Indentation patterns
   - Context (explanation vs. example)
3. Convert informal lists to proper markdown `-` lists
4. Standardize spacing: blank line before/after examples

**Tools Needed:**
- `paragraph_fixer.py` - NLP-based paragraph joining
- Pattern recognition for list structures

### 3. Page Markers and Artifacts (Medium Priority)

**Issues:**
- Some page markers remain (especially in footnotes)
- Section headers with embedded page numbers
- Running headers not fully removed

**Strategy:**
1. Find all remaining patterns: `§ 20-21 | RULES OF SANDHI. 15`
2. Remove page numbers from section headers
3. Clean up footerNote references
4. Remove cross-reference artifacts

**Tools Needed:**
- Enhanced regex patterns in cleanup script
- Manual review of edge cases

### 4. Markdown Structure Improvements (High Priority)

**Issues:**
- Inconsistent heading hierarchy
- Tables not in markdown table format
- No blockquotes for important notes/rules
- Code blocks not used for examples

**Strategy:**
1. Audit entire heading structure:
   - `#` - Book parts (Preface, Chapters, Appendices)
   - `##` - Major sections
   - `###` - Subsections
   - `####` - Rules/paragraphs (§ markers)

2. Convert tables to proper markdown:
   ```
   | Header 1 | Header 2 |
   |----------|----------|
   | Cell 1   | Cell 2   |
   ```

3. Use blockquotes for Pāṇini sūtras:
   ```
   > @[paraḥ sannikarṣaḥ saṃhitā] | Pāṇ. 1. 4. 109.
   ```

4. Use code blocks for paradigms/conjugation tables

**Tools Needed:**
- `structure_improver.py` - hierarchical heading analysis
- Manual table identification and conversion

### 5. Cross-References and Navigation (Low Priority)

**Issues:**
- Internal references not linked ("vide § 23")
- No anchor links for sections
- Index terms not tagged

**Strategy:**
1. Convert references to markdown links:
   - `vide § 23` → `(see [§ 23](#s-23))`
2. Add anchor IDs to all headings
3. Create internal link index
4. Add "back to top" links for long sections

**Tools Needed:**
- `link_generator.py` - automatic cross-reference linking

### 6. Content Validation (Ongoing)

**Issues:**
- Potential OCR errors in Sanskrit text
- Missing footnotes or broken footnote markers
- Incomplete examples

**Strategy:**
1. Spot-check against original PDF
2. Validate Sanskrit grammar examples
3. Check footnote integrity
4. Verify all Devanagari script rendered correctly

**Tools Needed:**
- Manual review
- Diff checker against original

## Implementation Phases

### Phase 1: Core Standardization (Current)
**Goal:** Clean, consistent, navigable markdown document

**Tasks:**
1. ✅ Initial cleanup and aggregation
2. ✅ First standardization pass
3. 🔄 Sanskrit term standardization (next)
4. ⬜ Paragraph flow fixes
5. ⬜ Remove all artifacts

**Deliverable:** `kales_sanskrit_grammar_clean.md`

### Phase 2: Structure Enhancement
**Goal:** Proper markdown structure for parsing and navigation

**Tasks:**
1. ⬜ Heading hierarchy audit and fix
2. ⬜ Table conversion to markdown
3. ⬜ Blockquotes for sūtras and important rules
4. ⬜ Code blocks for paradigms
5. ⬜ List formatting standardization

**Deliverable:** `kales_sanskrit_grammar_structured.md`

### Phase 3: Navigation and Links
**Goal:** Fully navigable digital edition

**Tasks:**
1. ⬜ Internal cross-reference linking
2. ⬜ Anchor IDs for all sections
3. ⬜ Table of contents with links
4. ⬜ Index generation

**Deliverable:** `kales_sanskrit_grammar_final.md`

### Phase 4: Validation and Polish
**Goal:** Publication-ready digital edition

**Tasks:**
1. ⬜ Content validation against PDF
2. ⬜ Sanskrit accuracy check
3. ⬜ Formatting consistency audit
4. ⬜ Generate HTML/PDF versions
5. ⬜ Add metadata (YAML front matter)

**Deliverable:** `kales_sanskrit_grammar_v1.0.md`

## Next Immediate Steps

1. **Create Sanskrit Standardization Script**
   - Build comprehensive term dictionary
   - Implement intelligent tagging logic
   - Handle edge cases (Devanagari, formulas, etc.)

2. **Run Sanskrit Standardization**
   - Process entire document
   - Review sample sections
   - Commit changes

3. **Fix Remaining Paragraphs**
   - More intelligent joining logic
   - Handle special cases (TOC, lists, tables)
   - Manual review of joins

4. **Structure Audit**
   - Map all headings
   - Verify hierarchy makes sense
   - Fix inconsistencies

## Success Metrics

- **Completeness:** All 728 pages represented
- **Consistency:** 100% Sanskrit terms tagged with @[...]
- **Structure:** Proper h1-h4 hierarchy throughout
- **Navigability:** All cross-references linked
- **Accuracy:** <0.1% OCR errors
- **Readability:** Clean, professional formatting

## Tools Repository

All scripts in `/Users/skmnktl/Downloads/ocr/`:
- ✅ `ocr_pages.py` - OCR extraction
- ✅ `create_chunks.py` - Chunk creation
- ✅ `cleanup_chunks.sh` - Claude cleanup
- ✅ `aggregate_cleaned_chunks.py` - Aggregation
- ✅ `standardize_format_v2.py` - Current standardization
- ⬜ `sanskrit_standardizer.py` - Next tool to create
- ⬜ `paragraph_fixer.py` - Paragraph flow fixes
- ⬜ `structure_improver.py` - Markdown structure
- ⬜ `link_generator.py` - Cross-reference linking
