# AST-Ready Markup Specification for Sanskrit Grammar v2

**Document:** Kale's "A Higher Sanskrit Grammar" (1894)  
**Version:** 8.0  
**Goal:** Machine-readable, AST-parseable structured markup  
**Date:** 2025-10-23  
**Architecture:** File-per-rule with folder structure + front matter

---

## Philosophy

**Separation of Concerns:**

1. **Folder Structure** = Document hierarchy (chapters, sections)
2. **Front Matter (YAML)** = Structural metadata (rule numbers, titles, pages)
3. **Content (Markdown)** = Semantic markup (grammar rules, examples, citations)

**Core Principle:** Structure lives in file system and front matter. Content contains only semantic meaning.

---

## File Organization

### Directory Structure

```
v8_sections/
├── 00_front/
│   ├── preface.md
│   └── toc.md
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

### Naming Conventions

- **Chapters:** `01_alphabet/`, `02_sandhi/`, `03_declension/`
- **Sections:** `01_svarasandhi/`, `02_halsandhi/`
- **Files:** `s019.md` (s = section, 019 = sequence number)

---

## Front Matter (YAML)

### Purpose
Structural metadata that can be **mechanically extracted** from v7. No AI interpretation needed.

### Required Fields

```yaml
---
rule: "§19"
title: "Vowel Coalescence Rule"
page: 12
---
```

### Field Definitions

| Field | Type | Source | Example | Required |
|-------|------|--------|---------|----------|
| `rule` | string | § marker from v7 | `"§19"` | Yes (if present) |
| `title` | string | Heading text | `"Vowel Coalescence Rule"` | Yes |
| `page` | integer | Original page number | `12` | Optional |

### Extraction Rules

- `rule`: Extract from pattern `#### § \d+\.` 
- `title`: Extract from heading after rule number, or infer from content
- `page`: Optional, from original PDF page numbers if tracked

### Example Files

**Grammar Rule:**
```yaml
---
rule: "§19"
title: "Vowel Coalescence Rule"
page: 12
---
```

**Paradigm Table:**
```yaml
---
rule: "§61"
title: "rāma (masculine a-stem)"
page: 35
---
```

**Section Without § Number:**
```yaml
---
title: "Abbreviations Used in the Work"
page: 8
---
```

---

## Content Markup (Semantic Only)

### 1. Sanskrit Markup

#### 1.1 Inline Sanskrit
```markdown
The rule of @[sandhi] applies when @[a] or @[ā] is followed by @[i].
```

**Rules:**
- ALL Sanskrit in IAST transliteration
- Proper diacritics: ā, ī, ū, ṛ, ṝ, ḷ, ṃ, ḥ, ñ, ṭ, ḍ, ṇ, ś, ṣ
- No spaces inside: `@[guṇa]` not `@[ guṇa ]`

#### 1.2 Block Sanskrit
```markdown
@:
paraḥ sannikarṣaḥ saṃhitā
:@
```

**Rules:**
- Multi-line Sanskrit passages
- IAST only
- No English mixed in

#### 1.3 Numbered Sanskrit (Verses)
```markdown
@line:
vartamāne laṭ vede leṭ
laṅ luṅ liṭas tathā
:@
```

**Rules:**
- Line breaks are semantic
- Used for verses, enumerated lists

#### 1.4 Mixed Sanskrit-English
```markdown
@:
sandhiḥ nityā'nityā dhātūpasargayoḥ
#[Sandhi is obligatory with roots and prepositions]#
nityā samāse vākye tu sā vivakṣām apekṣate
#[Obligatory in compounds, optional in sentences]#
:@
```

---

### 2. Grammar Rules

#### 2.1 Rule Declaration
```markdown
@rule{type: "sandhi.vowel.simple"}
```

**Attributes:**
- `type`: Hierarchical classification (dot-separated)

**Type Taxonomy:**
- `sandhi.vowel.simple`
- `sandhi.vowel.guna`
- `sandhi.consonant.nasal`
- `declension.noun.a-stem`
- `conjugation.verb.class-1`

**Note:** Rule ID (§ number) is in front matter, NOT here.

#### 2.2 Rule Statement
```markdown
When a simple vowel, short or long, is followed by a similar vowel, 
the substitute for them both is the similar long vowel.
```

Just plain text. No special markup for the rule statement itself.

---

### 3. Examples

#### 3.1 Single Example (Inline)
```markdown
@[upa] + @[indraḥ] → @[upendraḥ] "Viṣṇu"
```

**Format:**
- Use `→` (not `=`) for transformations
- Components in `@[...]` tags
- Gloss in quotes (optional)

#### 3.2 Example Block
```markdown
@examples{
  @[daitya] + @[ariḥ] → @[daityāriḥ]
  @[atra] + @[āsīt] → @[atrāsīt]
  @[vidyā] + @[āturaḥ] → @[vidyāturaḥ] "eager to gain knowledge"
}
```

**Rules:**
- One example per line
- No semicolons
- Quotes for glosses

---

### 4. Tables

#### 4.1 Declension Tables
```markdown
@declension{word: "rāma", gender: "masculine", stem: "a-stem"}

| Case | Singular | Dual | Plural |
|------|----------|------|--------|
| Nom. | @[rāmaḥ] | @[rāmau] | @[rāmāḥ] |
| Voc. | @[rāma]  | @[rāmau] | @[rāmāḥ] |
| Acc. | @[rāmam] | @[rāmau] | @[rāmān] |
```

**Metadata Attributes:**
- `word`: Base word
- `gender`: masculine/feminine/neuter
- `stem`: Stem type (a-stem, i-stem, etc.)

#### 4.2 Conjugation Tables
```markdown
@conjugation{root: "bhū", class: 1, pada: "parasmaipada"}

| Person | Singular | Dual | Plural |
|--------|----------|------|--------|
| 3rd    | @[bhavati] | @[bhavataḥ] | @[bhavanti] |
| 2nd    | @[bhavasi] | @[bhavathaḥ] | @[bhavatha] |
| 1st    | @[bhavāmi] | @[bhavāvaḥ] | @[bhavāmaḥ] |
```

**Metadata Attributes:**
- `root`: Verbal root
- `class`: 1-10
- `pada`: parasmaipada/ātmanepada

---

### 5. Citations & References

#### 5.1 Citations
```markdown
@cite{Pāṇini:VI.1.77}
@cite{Siddhānta-Kaumudī}
@cite{Kāśikā-Vṛtti}
```

**Format:**
- `Work:Reference` with colon separator
- No spaces around colon
- Proper IAST diacritics in work names

#### 5.2 Cross-References
```markdown
(see §20.a)
@xref{§23.8}
```

**Format:**
- `§` symbol required
- No spaces: `§23.8` not `§ 23. 8`

#### 5.3 Footnotes
```markdown
[^1]: @:
paraḥ sannikarṣaḥ saṃhitā
:@ — @cite{Pāṇini:1.4.109}
```

**Format:**
- Standard markdown footnotes `[^n]`
- Sanskrit in block format if needed
- Citation at end after `—`

---

## What NOT to Include

### ❌ Removed from Content

**Structural elements (now in folder/front matter):**
- ❌ `@chapter{...}` (use folder path)
- ❌ `@section{...}` (use folder path)
- ❌ `id: "§19"` in `@rule{}` (use front matter `rule:`)
- ❌ Section titles in content (use front matter `title:`)

**Visual formatting (not semantic):**
- ❌ Horizontal rules `---`
- ❌ Page numbers
- ❌ Double spaces
- ❌ Asterisk/dagger footnotes (`*`, `†`) - use `[^n]`

---

## Complete File Example

### Path
```
v8_sections/02_sandhi/01_svarasandhi/s019.md
```

### Content
```yaml
---
rule: "§19"
title: "Vowel Coalescence Rule"
page: 12
---

@rule{type: "sandhi.vowel.simple"}

When a simple vowel, short or long, is followed by a similar vowel, 
the substitute for them both is the similar long vowel.

@examples{
  @[daitya] + @[ariḥ] → @[daityāriḥ]
  @[atra] + @[āsīt] → @[atrāsīt]
  @[vidyā] + @[āturaḥ] → @[vidyāturaḥ] "eager to gain knowledge"
}

[^1]: @:
paraḥ sannikarṣaḥ saṃhitā
:@ — @cite{Pāṇini:1.4.109}
```

---

## AST Generation

### Parse Hierarchy

```python
# Path: v8_sections/02_sandhi/01_svarasandhi/s019.md

ast_node = {
  "location": {
    "chapter": "02_sandhi",
    "section": "01_svarasandhi", 
    "file": "s019.md",
    "sequence": 19
  },
  "metadata": {
    "rule": "§19",
    "title": "Vowel Coalescence Rule",
    "page": 12
  },
  "content": {
    "type": "sandhi.vowel.simple",
    "statement": "When a simple vowel...",
    "examples": [
      {"from": ["daitya", "ariḥ"], "to": "daityāriḥ"},
      ...
    ],
    "footnotes": [
      {"sanskrit": "paraḥ...", "cite": "Pāṇini:1.4.109"}
    ]
  }
}
```

---

## Processing Instructions for Claude

### Input
Claude receives one file at a time with:
- Path (for context)
- Front matter (unchanged)
- Content from v7 (needs semantic markup)

### Output
Claude returns:
- Front matter (UNCHANGED)
- Content with semantic markup added

### Claude's Tasks

✅ **DO:**
1. Convert all Sanskrit to IAST
2. Tag all Sanskrit terms with `@[...]`
3. Use `@:...:@` for Sanskrit blocks
4. Replace `=` with `→` in transformations
5. Add `@rule{type: "..."}` with classification
6. Structure examples as `@examples{...}`
7. Convert citations to `@cite{Work:Ref}`
8. Convert footnotes to `[^n]` format
9. Remove OCR errors, fix spacing
10. Remove horizontal rules `---`

❌ **DON'T:**
1. Modify front matter
2. Add structural tags (`@chapter`, `@section`)
3. Change Victorian-era English
4. Modernize terminology
5. Remove examples
6. Alter Sanskrit content

---

## Validation Checklist

For each processed file:

- ✅ Front matter unchanged
- ✅ All Sanskrit in IAST
- ✅ All Sanskrit tagged `@[...]`
- ✅ Examples use `→` not `=`
- ✅ `@rule{type: "..."}` present
- ✅ Citations as `@cite{...}`
- ✅ Footnotes as `[^n]`
- ✅ No OCR errors
- ✅ No horizontal rules
- ✅ No structural tags in content

---

## Quick Reference

### Sanskrit
```markdown
@[inline]              # Inline Sanskrit
@: block :@            # Block Sanskrit
@line: verses :@       # Numbered verses
#[English]#            # English in Sanskrit blocks
```

### Grammar
```markdown
@rule{type: "..."}         # Rule classification
@examples{...}              # Example block
@declension{word: "..."}   # Declension table
@conjugation{root: "..."}  # Conjugation table
```

### Citations
```markdown
@cite{Work:Ref}        # Citation
@xref{§X.Y}            # Cross-reference
[^n]: ...              # Footnote
```

### Transformations
```markdown
@[a] + @[b] → @[c]     # Use → not =
```

---

**End of Specification v2**
