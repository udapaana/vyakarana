# v8 Processing Architecture: Design Decisions

**Date:** 2025-10-23
**Status:** ✅ **FINALIZED**
**Decision:** File per § rule with folder structure + front matter for structural metadata

---

## The Question

When splitting v7 into sections for parallel Claude processing, what's the optimal file granularity?

### Options Being Considered

1. **File per § rule** (~600 files)
2. **File per major section** (~30-40 files) — Currently proposed
3. **File per chapter** (~17 files)
4. **Something in between**

---

## Option 1: File Per § Rule (Very Fine-Grained)

### Structure

```
v8_sections/
├── 02_sandhi/
│   ├── rule_018.md  # § 18. By sandhi...
│   ├── rule_019.md  # § 19. If a simple vowel...
│   ├── rule_020.md  # § 20. When a or ā...
│   ├── rule_021.md  # § 21. When a or ā followed by e...
│   └── ... (600+ more)
```

### Pros

✅ **Maximum Parallelization**: Process 50-100 rules simultaneously
✅ **Granular Git History**: Each rule change tracked separately
✅ **Easy Rollback**: Bad processing? Revert single rule
✅ **Surgical Edits**: Fix one rule without touching others
✅ **Database-Ready**: One file = one database record

### Cons

❌ **Context Loss**: Rules reference each other ("as in § 19 above")
❌ **File Explosion**: 600+ files to manage
❌ **Complex Assembly**: Reassembly order becomes critical
❌ **Cross-Reference Challenges**: Need to track references across files
❌ **Examples Span Rules**: Multi-rule examples get split
❌ **Overhead**: 600 file I/O operations
❌ **Claude Context**: Each rule processed in isolation (loses pedagogical flow)

### Analysis

This is **too granular** for a grammar textbook where:

- Rules build on each other
- Examples illustrate multiple related rules
- Exceptions reference parent rules
- Pedagogical structure matters

**Verdict:** ❌ Not recommended for initial processing

---

## Option 2: File Per Major Section (Current Proposal)

### Structure

```
v8_sections/
├── 02_sandhi/
│   ├── 01_svarasandhi.md      # §18-27 (vowel sandhi, ~300 lines)
│   ├── 02_halsandhi.md        # §28-44 (consonant sandhi, ~400 lines)
│   └── 03_visargasandhi.md    # §45-50 (visarga sandhi, ~200 lines)
├── 03_declension/
│   ├── 01_vowel_stems.md      # a, ā, i, ī, u, ū stems (~800 lines)
│   ├── 02_consonant_stems.md  # n, r, s stems (~600 lines)
│   └── 03_irregular.md        # Special cases (~400 lines)
└── ... (~30-40 total files)
```

### Pros

✅ **Context Preserved**: Related rules stay together
✅ **Manageable**: 30-40 files (reviewable, trackable)
✅ **Still Parallel**: Process 5-10 sections simultaneously
✅ **Logical Units**: Matches textbook structure
✅ **Claude Benefits**: Full context for related rules
✅ **Git-Friendly**: Reasonable diff sizes
✅ **Cross-References**: Most refs stay within file

### Cons

⚠️ **Some Large Files**: Conjugation chapter might be 2000+ lines
⚠️ **Less Granular History**: Changes to multiple rules in one commit
⚠️ **Partial Parallelization**: Only ~30 units vs 600

### Analysis

This is a **sweet spot** that:

- Maintains pedagogical coherence
- Enables meaningful parallelization
- Keeps context for Claude to do quality work
- Matches human mental model of the content

**Verdict:** ✅ **Recommended**

---

## Option 3: File Per Chapter (Coarse-Grained)

### Structure

```
v8_sections/
├── 01_alphabet.md         # All of Chapter I (~200 lines)
├── 02_sandhi.md          # All sandhi rules (~900 lines)
├── 03_declension.md      # All declensions (~2000 lines)
├── 11_conjugation.md     # All verbs (~4000 lines!)
└── ... (~17 total files)
```

### Pros

✅ **Maximum Context**: Entire chapter available
✅ **Minimal Assembly**: Just concatenate in order
✅ **Simple Management**: Only ~17 files
✅ **Natural Units**: Matches original book structure

### Cons

❌ **Limited Parallelization**: Only ~17 concurrent tasks
❌ **Huge Files**: Conjugation = 4000 lines (too big for single Claude call)
❌ **Large Diffs**: Hard to review changes
❌ **Long Processing**: Each file takes 2-5 minutes
❌ **Memory Issues**: Large context windows

### Analysis

This is **too coarse** because:

- Some chapters are too large for efficient processing
- Limits parallelization benefits
- Makes incremental progress harder to track

**Verdict:** ❌ Not optimal for parallel processing

---

## Option 4: Hybrid - File Per Logical Teaching Unit

### Structure

```
v8_sections/
├── 02_sandhi/
│   ├── 01_simple_vowel_sandhi.md    # §18-22 (basic vowel rules)
│   ├── 02_complex_vowel_sandhi.md   # §23-27 (exceptions, special cases)
│   ├── 03_consonant_sandhi.md       # §28-40 (most consonant rules)
│   ├── 04_special_consonants.md     # §41-44 (ṇ, ṣ retroflexion)
│   └── 05_visarga.md                # §45-50 (all visarga rules)
├── 03_declension/
│   ├── 01_a_stems.md                # Just a/ā stems
│   ├── 02_i_stems.md                # Just i/ī stems
│   ├── 03_u_stems.md                # Just u/ū stems
│   ├── 04_r_stems.md                # Just ṛ stems
│   ├── 05_consonant_stems.md        # n, r, s stems
│   └── 06_irregular.md              # Special cases
└── ... (~40-50 total files)
```

### Pros

✅ **Pedagogically Sound**: Each file = one concept
✅ **Balanced Size**: 150-400 lines per file (sweet spot)
✅ **Good Parallelization**: 40-50 concurrent tasks possible
✅ **Easy Review**: Each file reviewable in 5-10 minutes
✅ **Meaningful Units**: "I'm working on i-stem declensions"
✅ **Claude-Friendly**: Enough context, not overwhelming

### Cons

⚠️ **More Files**: ~50 files vs ~30
⚠️ **Subjective Splits**: Requires judgment on "logical units"
⚠️ **Some Overlap**: Where to split related concepts?

### Analysis

This **refines Option 2** by:

- Breaking very large sections into teachable units
- Keeping very cohesive sections together
- Optimizing for human comprehension AND machine processing

**Verdict:** ✅ **Best compromise** (slightly more granular than Option 2)

---

## Key Trade-Offs Summary

| Criterion            | Per-Rule (600) | Per-Section (30) | Per-Chapter (17) | Hybrid (50)  |
| -------------------- | -------------- | ---------------- | ---------------- | ------------ |
| Context Preservation | ❌ Poor        | ✅ Good          | ✅ Excellent     | ✅ Good      |
| Parallelization      | ✅ Max         | ✅ Good          | ❌ Limited       | ✅ Good+     |
| File Management      | ❌ Hard        | ✅ Easy          | ✅ Very Easy     | ✅ Easy      |
| Review Difficulty    | ⚠️ Fragmented  | ✅ Reasonable    | ⚠️ Large         | ✅ Easy      |
| Git History          | ✅ Granular    | ✅ Good          | ❌ Coarse        | ✅ Good      |
| Claude Quality       | ❌ No context  | ✅ Good          | ✅ Best          | ✅ Good      |
| Processing Time      | ✅ 10-15 min   | ✅ 15-20 min     | ❌ 30-40 min     | ✅ 15-20 min |

---

## Recommendation

### **Go with Hybrid (Option 4)**

**Rationale:**

1. **Context**: Claude gets enough related rules to understand patterns
2. **Parallelization**: 40-50 files = 5-10 parallel workers at a time
3. **Reviewability**: Each file is a digestible chunk
4. **Logical Units**: Matches how humans think about grammar
5. **Flexibility**: Can further split if needed

### Specific Split Guidelines

**When to split:**

- ✅ Different stem types (a-stems vs i-stems)
- ✅ Different rule categories (simple vs exceptions)
- ✅ Natural pedagogical breaks
- ✅ File would exceed ~500 lines

**When to keep together:**

- ✅ Tightly coupled rules (exception to its parent rule)
- ✅ Example-heavy sections (examples lose meaning without rules)
- ✅ Short sections (<200 lines)
- ✅ Progressive complexity (basic → advanced within same topic)

---

## Processing Strategy with Hybrid Approach

### Phase 1: Extract (~50 files)

```python
# Each file: 150-500 lines
# Total time: ~1 minute
```

### Phase 2: Process (Parallel)

```python
# 10 workers × 5 batches = ~15 minutes
# With retries: ~20 minutes total
```

### Phase 3: Validate

```python
# Parallel validation: ~2 minutes
```

### Phase 4: Assemble

```python
# Sequential assembly: ~30 seconds
```

**Total end-to-end: ~25 minutes** (vs 2+ hours sequential)

---

## Decision Log

- **2025-10-23**: Initial proposal for ~30 files (Option 2)
- **2025-10-23**: Discussion → prefer ~50 files (Option 4 - Hybrid)
- **Next**: Finalize split points and implement

---

## Questions for Consideration

1. **Should tables be in separate files?**
   - Large paradigm tables (declensions, conjugations)
   - Currently: Keep with rules (context)
   - Alternative: Split out (reusable)

2. **How to handle cross-chapter references?**
   - Example: Conjugation references sandhi rules
   - Current: Keep references as `@xref{§X}`
   - Processing: Each file sees references, doesn't resolve them

3. **What about the verb index (Dhātukosha)?**
   - ~2000 lines of tabular data
   - Option A: One file (easy)
   - Option B: Split by letter (a-ka, kha-ga, etc.)
   - Recommendation: One file (pure data, minimal processing needed)

4. **Footnotes stay with sections or separate?**
   - Current proposal: Stay with section
   - Benefit: Context preserved
   - Assembly: Footnote numbers might need renumbering

---

## Next Steps

1. ✅ Document architecture decision (this file)
2. ⏳ Finalize exact split points (create detailed section_config.yaml)
3. ⏳ Implement extract_sections.py
4. ⏳ Implement process_sections_parallel.py
5. ⏳ Test on 2-3 sections before full run
6. ⏳ Full processing run

---

## FINAL DECISION: File Per § Rule + Structural Metadata

**Date:** 2025-10-23  
**Status:** ✅ Adopted

### Key Insight

By using **folder structure + front matter** for structural metadata, we eliminate the need for Claude to have multi-rule context. Each file can be processed independently.

### Architecture

```
v8_sections/
├── 01_alphabet/
│   ├── s001.md
│   └── s002.md
├── 02_sandhi/
│   ├── 01_svarasandhi/
│   │   ├── s018.md
│   │   ├── s019.md
│   │   └── s020.md
│   ├── 02_halsandhi/
│   │   └── s028.md
│   └── 03_visargasandhi/
│       └── s045.md
└── 03_declension/
    ├── 01_vowel_stems/
    │   ├── 01_a_stems/
    │   │   └── s061.md
    │   └── 02_i_stems/
    │       └── s068.md
    └── 02_consonant_stems/
        └── s092.md
```

### File Format

**Path:** `v8_sections/02_sandhi/01_svarasandhi/s019.md`

**Front Matter (Structural - Mechanical):**
```yaml
---
rule: "§19"
title: "Vowel Coalescence Rule"
page: 12
---
```

**Content (Semantic - AI-Added):**
```markdown
@rule{type: "sandhi.vowel.simple"}

When a simple vowel, short or long, is followed by a similar vowel, 
the substitute for them both is the similar long vowel.

@examples{
  @[daitya] + @[ariḥ] → @[daityāriḥ]
  @[atra] + @[āsīt] → @[atrāsīt]
}

[^1]: @:
paraḥ sannikarṣaḥ saṃhitā
:@ — @cite{Pāṇini:1.4.109}
```

### Information Architecture

| Information Type | Storage Location | Generated By | Example |
|-----------------|------------------|--------------|---------|
| Chapter hierarchy | Folder path | Mechanical script | `02_sandhi/` |
| Section hierarchy | Folder path | Mechanical script | `01_svarasandhi/` |
| Rule sequence | Filename | Mechanical script | `s019.md` |
| Rule number | Front matter | Mechanical script | `rule: "§19"` |
| Rule title | Front matter | Mechanical script | `title: "Vowel..."` |
| Original page | Front matter | Mechanical script | `page: 12` |
| Rule classification | Content | Claude (AI) | `@rule{type: "..."}` |
| Examples | Content | Claude (AI) | `@examples{...}` |
| Citations | Content | Claude (AI) | `@cite{...}` |

### Why This Works

1. **No Redundancy**: Each piece of info appears exactly once
   - Rule number in front matter (not in content)
   - Title in front matter (not in content)
   - Chapter/section in folder path (not in front matter or content)

2. **Separation of Concerns**:
   - **Folder structure** = Document hierarchy
   - **Front matter** = Minimal structural metadata
   - **Content** = Pure semantic markup (AST-parseable)

3. **Mechanical Extraction**: Front matter can be generated by simple Python script
   - No AI needed for structural metadata
   - No hallucination risk
   - 100% consistent

4. **Independent Processing**: Each file is self-contained
   - Claude doesn't need surrounding context
   - Process 50-100 files in parallel
   - Total processing time: 2-3 minutes

5. **Easy Assembly**: Combine in order
   ```python
   for file in sorted(glob("v8_sections/**/*.md")):
       frontmatter = parse_yaml(file)
       content = parse_markdown(file)
       # Insert title from frontmatter, append content
   ```

### Processing Pipeline

```
┌─────────────────────┐
│  v7 Input           │
│  (single file)      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 1. EXTRACT          │ Python script
│ → ~600 .md files    │ Mechanically split by § markers
│ → Folder structure  │ Create nested directories
│ → Front matter      │ Extract rule #, title, page
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 2. PROCESS          │ Claude API (parallel)
│ → Add @rule{}       │ 50-100 concurrent workers
│ → Add @examples{}   │ Per MARKUP_SPECIFICATION
│ → Add @cite{}       │ Front matter unchanged
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 3. VALIDATE         │ Python + regex
│ → Check @rule{}     │ Verify markup compliance
│ → Check @cite{}     │ Validate references
│ → Flag errors       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 4. ASSEMBLE         │ Python script
│ → Combine by order  │ Sort by path + sequence
│ → Insert titles     │ From front matter
│ → Generate v8.md    │ Single output file
└─────────────────────┘
```

### Benefits Summary

✅ **Massive Parallelization**: 600 files = 600 independent tasks  
✅ **No Context Needed**: All structural info in path + front matter  
✅ **Consistent Metadata**: Generated mechanically, zero variation  
✅ **Git-Friendly**: One rule = one file = granular version control  
✅ **AST-Ready**: Path + front matter + content = complete AST node  
✅ **Fast Processing**: 2-3 minutes total (vs 2+ hours sequential)  
✅ **Easy Review**: Each file is 10-50 lines (digestible)  
✅ **Surgical Fixes**: Reprocess single rule without touching others  

### Estimated Counts

- **Total files**: ~600
- **Chapters**: 15-17 folders
- **Sections**: 40-50 folders
- **Rules/Paradigms**: ~600 .md files
- **Processing time**: 2-3 minutes (50 parallel workers)
- **Review time**: ~20 hours (reviewing each file individually)

---

## Decision Rationale

The key breakthrough was realizing that **front matter + folder structure eliminates the need for Claude to have multi-rule context**. 

Previously thought:
- ❌ "Claude needs to see multiple related rules to understand patterns"

Actually:
- ✅ "With explicit front matter, each rule is self-contained"
- ✅ "Folder path tells us chapter/section"
- ✅ "Front matter tells us rule number and title"
- ✅ "Claude just adds semantic markup to content"

This enables:
1. File-per-rule granularity (maximum parallelization)
2. Without context loss (structural metadata compensates)
3. With consistent results (no AI in metadata generation)

---

## Next Steps

1. ✅ Update ARCHITECTURE_DECISIONS.md (this file)
2. ⏳ Update MARKUP_SPECIFICATION.md with front matter guidelines
3. ⏳ Implement extract_sections.py (~200 lines)
4. ⏳ Implement process_parallel.py (~250 lines)
5. ⏳ Implement validate_ast.py (~150 lines)
6. ⏳ Implement assemble_v8.py (~100 lines)
7. ⏳ Test on 5-10 files before full run
8. ⏳ Full processing run

