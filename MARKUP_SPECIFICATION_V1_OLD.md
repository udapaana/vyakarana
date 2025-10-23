# AST-Ready Markup Specification for Sanskrit Grammar

**Document:** Kale's "A Higher Sanskrit Grammar" (1894)
**Version:** 8.0
**Goal:** Machine-readable, AST-parseable structured markup
**Date:** 2025-10-23

---

## Philosophy

This markup language prioritizes **semantic structure over visual formatting**. Every element must be machine-parseable to enable:

- AST (Abstract Syntax Tree) generation
- Programmatic analysis and querying
- Database storage with relationships
- Interactive web applications
- Multiple output formats (JSON, GraphQL, SQL)

**Core Principle:** If it has meaning, tag it. If it's just visual, remove it.

---

## 1. Sanskrit Content Markup

### 1.1 Inline Sanskrit
**Purpose:** Words, terms, short phrases embedded in English text
**Format:** `@[sanskrit_text_in_IAST]`

```markdown
The rule of @[sandhi] applies when @[a] or @[ā] is followed by @[i].
```

**Rules:**
- ALL Sanskrit must be in IAST transliteration (no Devanagari inline)
- Proper diacritics required: ā, ī, ū, ṛ, ṝ, ḷ, ṃ, ḥ, ñ, ṭ, ḍ, ṇ, ś, ṣ
- No spaces inside brackets: `@[guṇa]` not `@[ guṇa ]`

### 1.2 Block Sanskrit
**Purpose:** Continuous Sanskrit text (sūtras, verses, quotations)
**Format:** `@: ... :@`

```markdown
@:
paraḥ sannikarṣaḥ saṃhitā
:@
```

**Rules:**
- Multi-line Sanskrit passages
- IAST transliteration only
- No English mixed in (use 1.4 for that)

### 1.3 Numbered Block Sanskrit
**Purpose:** Verses, enumerated lists, or line-by-line examples
**Format:** `@line: ... :@`

```markdown
@line:
vartamāne laṭ vede leṭ
laṅ luṅ liṭas tathā
vidhyāśiṣos tu liṅ loṭo
luṭ lṛṭ lṛṅ ca bhaviṣyati
:@
```

**Rules:**
- Line breaks are semantically significant
- IAST transliteration
- Used for verses, paradigms, or numbered sequences

### 1.4 Mixed Sanskrit-English Blocks
**Purpose:** Sanskrit text with interlinear English glosses/explanations
**Format:** `@: sanskrit #[english]# sanskrit :@`

```markdown
@:
sandhiḥ nityā'nityā dhātūpasargayoḥ
#[Sandhi is obligatory with roots and prepositions]#
nityā samāse vākye tu sā vivakṣām apekṣate
#[Obligatory in compounds, optional in sentences]#
:@
```

**Rules:**
- English commentary enclosed in `#[...]#`
- Sanskrit portions in IAST
- Use sparingly, prefer separate translation blocks

---

## 2. Structural Elements

### 2.1 Document Metadata
**Purpose:** Top-level document information
**Format:** YAML front matter

```yaml
---
title: "A Higher Sanskrit Grammar"
author: "M. R. Kale"
year: 1894
edition: 1
place: "Bombay"
language: "English"
script: "IAST"
subject: "Sanskrit Grammar"
tradition: "Pāṇinian"
---
```

### 2.2 Chapter
**Purpose:** Major document division
**Format:** `@chapter{key: value, ...}`

```markdown
@chapter{id: "II", title: "Rules of Sandhi", page: 11}

# CHAPTER II

## RULES OF SANDHI
```

**Attributes:**
- `id`: Roman numeral or sequential identifier
- `title`: Full chapter title
- `page`: Original page number (optional, for reference)

### 2.3 Section
**Purpose:** Subdivisions within chapters
**Format:** `@section{...}`

```markdown
@section{id: "II.1", type: "svarasandhi", title: "Combination of Final and Initial Vowels"}

### I. SVARASANDHI, OR THE COMBINATION OF FINAL AND INITIAL VOWELS
```

**Attributes:**
- `id`: Hierarchical identifier (Chapter.Section)
- `type`: Classification/category
- `title`: Section heading

---

## 3. Grammatical Elements

### 3.1 Grammar Rule
**Purpose:** Formal grammatical rule statements
**Format:** `@rule{...}`

```markdown
@rule{id: "§19", type: "sandhi.vowel.simple", applies_to: "similar_vowels"}

#### § 19. Vowel Coalescence Rule

If a simple vowel, short or long, be followed by a similar vowel,
the substitute for them both is the similar long vowel.
```

**Attributes:**
- `id`: Unique section identifier (§ number)
- `type`: Hierarchical rule classification (dot-separated)
- `applies_to`: What the rule operates on (optional)
- `class`: Alternative classification

**Type Taxonomy Examples:**
- `sandhi.vowel.simple`
- `sandhi.consonant.visarga`
- `declension.noun.a-stem`
- `conjugation.verb.class-1`

### 3.2 Conditions & Results
**Purpose:** Formal specification of rule application
**Format:** Structured blocks

```markdown
@conditions{
  vowel1: "simple (short OR long)"
  vowel2: "similar to vowel1"
}

@result{
  vowel1 + vowel2 → "long vowel (similar)"
}
```

### 3.3 Exception
**Purpose:** Exceptions to a stated rule
**Format:** `@exception{to: "§X", condition: "..."}`

```markdown
@exception{to: "§20", condition: "when followed by ūha, ūhana, ūhya"}

Vṛddhi substitute takes place in the following cases:
(a) When a word ending in @[ā] is followed by @[ūha], @[ūhana], or @[ūhya]
```

### 3.4 Counter-Exception
**Purpose:** Exception to an exception
**Format:** `@counter_exception{to: "§20.exception.a"}`

```markdown
@counter_exception{to: "§21.a"}

If a form of the root @[i] to go comes after @[a], @[guṇa] takes place instead.
```

---

## 4. Examples

### 4.1 Single Example
**Purpose:** Illustrative transformation or usage
**Format:** Components with arrow notation and optional gloss

```markdown
@[upa] + @[indraḥ] → @[upendraḥ] "Viṣṇu"
@[kṛṣṇa] + @[uruḥ] → @[kṛṣṇoruḥ] "Kṛṣṇa's thigh"
```

**Rules:**
- Use `→` (U+2192) not `=` for transformations
- Components in `@[...]` tags
- Gloss in quotes after result (optional)
- No semicolons at end

### 4.2 Example Block
**Purpose:** Multiple related examples
**Format:** `@examples{...}`

```markdown
@examples{
  @[upa] + @[indraḥ] → @[upendraḥ] "Viṣṇu"
  @[parama] + @[īśvaraḥ] → @[parameśvaraḥ] "the great lord"
  @[ramā] + @[icchā] → @[ramecchā] "the wish of Rāmā"
  @[hita] + @[upadeśaḥ] → @[hitopadeśaḥ] "friendly instruction"
}
```

**Attributes (optional):**
- `type`: "sandhi", "declension", "formation"
- `rule`: Reference to rule being illustrated

---

## 5. Paradigms & Tables

### 5.1 Declension Table
**Purpose:** Noun/adjective paradigms
**Format:** `@declension{...}` + markdown table

```markdown
@declension{
  word: "rāma"
  gender: "masculine"
  stem: "a-stem"
  gloss: "Rāma (proper name)"
}

| Case | Singular | Dual | Plural |
|------|----------|------|--------|
| Nom. | @[rāmaḥ] | @[rāmau] | @[rāmāḥ] |
| Voc. | @[rāma]  | @ditto{Nom.Dual} | @ditto{Nom.Plural} |
| Acc. | @[rāmam] | @ditto{Nom.Dual} | @[rāmān] |
| Ins. | @[rāmeṇa] | @[rāmābhyām] | @[rāmaiḥ] |
| Dat. | @[rāmāya] | @ditto{Ins.Dual} | @[rāmebhyaḥ] |
| Abl. | @[rāmāt] | @ditto{Ins.Dual} | @ditto{Dat.Plural} |
| Gen. | @[rāmasya] | @[rāmayoḥ] | @[rāmāṇām] |
| Loc. | @[rāme] | @ditto{Gen.Dual} | @[rāmeṣu] |
```

**Attributes:**
- `word`: The base word being declined
- `gender`: masculine/feminine/neuter
- `stem`: Stem type (a-stem, i-stem, consonant-stem, etc.)
- `gloss`: English meaning

### 5.2 Conjugation Table
**Purpose:** Verb paradigms
**Format:** `@conjugation{...}` + markdown table

```markdown
@conjugation{
  root: "bhū"
  class: 1
  meaning: "to be, to become"
  pada: "parasmaipada"
}

| Person | Singular | Dual | Plural |
|--------|----------|------|--------|
| 3rd    | @[bhavati] | @[bhavataḥ] | @[bhavanti] |
| 2nd    | @[bhavasi] | @[bhavathaḥ] | @[bhavatha] |
| 1st    | @[bhavāmi] | @[bhavāvaḥ] | @[bhavāmaḥ] |
```

**Attributes:**
- `root`: Verbal root
- `class`: 1-10 (conjugation class)
- `meaning`: English translation
- `pada`: parasmaipada/ātmanepada/ubhayapada
- `tense`: present/imperfect/perfect/etc. (if specified)

### 5.3 Generic Tables
**Purpose:** Other tabular data
**Format:** `@table{type: "...", ...}`

```markdown
@table{type: "comparison", feature: "vowel_length"}

| Type | Short | Long | Protracted |
|------|-------|------|------------|
| a    | @[a]  | @[ā] | @[a³] |
| i    | @[i]  | @[ī] | @[i³] |
```

### 5.4 Ditto Marks
**Purpose:** Indicate repetition in tables
**Format:** `@ditto{source}`

```markdown
| Voc. | @[rāma] | @ditto{Nom.Dual} | @ditto{Nom.Plural} |
```

**Alternative:** Expand all values (removes visual convention but clearer for parsing)

---

## 6. Scholarly Apparatus

### 6.1 Footnotes
**Purpose:** Additional information, sources, clarifications
**Format:** Standard markdown footnotes `[^n]`

```markdown
The @[visarga] is not an original character.[^1]

[^1]: It is only a substitute for final @[r] or @[s].
```

**For Sanskrit sūtras in footnotes:**
```markdown
[^2]: @:
paraḥ sannikarṣaḥ saṃhitā
:@ — @cite{Pāṇini:1.4.109}
```

### 6.2 Citations
**Purpose:** References to source texts
**Format:** `@cite{Work:Reference}`

```markdown
@cite{Pāṇini:1.4.109}
@cite{Pāṇini:VI.1.77}
@cite{Siddhānta-Kaumudī}
@cite{Kāśikā-Vṛtti}
@cite{Mahābhāṣya}
@cite{Aṣṭādhyāyī:III.1.26}
```

**Format Rules:**
- Work name with proper IAST diacritics
- Colon separator
- Reference in standard notation (book.chapter.verse or I.ii.123)
- No spaces around colon

**Common Works (standardized names):**
- `Pāṇini` (for Aṣṭādhyāyī)
- `Siddhānta-Kaumudī`
- `Kāśikā-Vṛtti`
- `Mahābhāṣya`
- `Vārttika`

### 6.3 Cross-References
**Purpose:** Internal document references
**Format:** `@xref{§X.Y}` or inline `(see §X.Y)`

```markdown
The rule explained in @xref{§23.8} applies here.

This is optional (see §20.a) but mandatory in compounds.
```

**Format Rules:**
- `§` symbol required
- Section number format: `§19` or `§23.8` or `§20.a`
- No spaces: `§23.8` not `§ 23. 8`
- Subsections: letters (a, b, c) or numbers (1, 2, 3)

---

## 7. Special Elements

### 7.1 Notes
**Purpose:** Author's observations or clarifications
**Format:** Standard markdown with optional tag

```markdown
@note{type: "observation"}

**N.B.** The @[visarga] is not counted among the letters of the alphabet.
```

```markdown
@note{type: "explanation"}

**Note:** This explains why there are no names for the different letters.
```

### 7.2 Observations
**Purpose:** Special observations or comments
**Format:** `@obs{...}`

```markdown
@obs{id: "§111"}

**Obs.** The @[s] of @[uktha-śās] becomes @[ś] before consonantal terminations.
```

### 7.3 Translations
**Purpose:** English rendering of Sanskrit passages
**Format:** `@translation{...}`

```markdown
@line:
vartamāne laṭ vede leṭ
laṅ luṅ liṭas tathā
:@

@translation{
For present tense, @[laṭ]; in Vedic, @[leṭ]; @[laṅ], @[luṅ], and @[liṭ] likewise.
}
```

### 7.4 Lists
**Purpose:** Structured lists (not tables)
**Format:** Standard markdown with optional metadata

```markdown
@list{type: "enumeration", ordered: true}

The five classes are:
1. @[kavarga]: @[k], @[kh], @[g], @[gh], @[ṅ]
2. @[cavarga]: @[c], @[ch], @[j], @[jh], @[ñ]
3. @[ṭavarga]: @[ṭ], @[ṭh], @[ḍ], @[ḍh], @[ṇ]
4. @[tavarga]: @[t], @[th], @[d], @[dh], @[n]
5. @[pavarga]: @[p], @[ph], @[b], @[bh], @[m]
```

---

## 8. Removed Elements

### What We DELETE (Visual Formatting Only)

❌ **Horizontal rules** (`---`)
   → Replace with semantic section boundaries

❌ **Page numbers** (OCR artifacts)
   → Optional: Keep in metadata `@chapter{..., page: 11}`

❌ **Double spaces** (formatting errors)
   → Fix to single space

❌ **Asterisk/dagger footnote markers** (`*`, `†`, `‡`)
   → Replace with `[^n]` numbered footnotes

❌ **Ditto marks** (optional)
   → Either expand: `@[rāmau]` or tag: `@ditto{Nom.Dual}`

❌ **Visual separators between footnotes**
   → Footnote blocks handle separation semantically

---

## 9. Complete Transformation Example

### BEFORE (v7)

```markdown
#### § 20. When @[a] or @[ā] is followed by @[i], @[ī], @[u], @[ū], short or long, the @[guṇa] letter corresponding to the latter takes the place of both; e.g. @[upa] + @[indraḥ] = @[upendraḥ] Viṣṇu; @[parama] + @[īśvaraḥ] = @[parameśvaraḥ] the great lord; @[ramā] + @[icchā] = @[ramecchā] the wish of Rāmā.

* @[iko yaṇ] Pāṇ. VI. 1. 77.

---
```

### AFTER (v8 - AST-Ready)

```markdown
@rule{id: "§20", type: "sandhi.vowel.guna", applies_to: "a/ā + i/ī/u/ū"}

#### § 20. Guṇa Substitution Rule

When @[a] or @[ā] is followed by @[i], @[ī], @[u], or @[ū] (short or long),
the @[guṇa] letter corresponding to the latter takes the place of both.

@examples{
  @[upa] + @[indraḥ] → @[upendraḥ] "Viṣṇu"
  @[parama] + @[īśvaraḥ] → @[parameśvaraḥ] "the great lord"
  @[ramā] + @[icchā] → @[ramecchā] "the wish of Rāmā"
}

[^20.1]: @:
iko yaṇ
:@ — @cite{Pāṇini:VI.1.77}
```

---

## 10. AST Output Schema

With this markup, we can generate structured output:

### JSON Schema Example

```json
{
  "rule": {
    "id": "§20",
    "type": "sandhi.vowel.guna",
    "applies_to": "a/ā + i/ī/u/ū",
    "statement": "When a or ā is followed by i, ī, u, or ū...",
    "examples": [
      {
        "components": ["upa", "indraḥ"],
        "result": "upendraḥ",
        "gloss": "Viṣṇu"
      },
      {
        "components": ["parama", "īśvaraḥ"],
        "result": "parameśvaraḥ",
        "gloss": "the great lord"
      }
    ],
    "footnotes": [
      {
        "id": "20.1",
        "sanskrit": ["iko yaṇ"],
        "citation": {
          "work": "Pāṇini",
          "reference": "VI.1.77"
        }
      }
    ]
  }
}
```

---

## 11. Implementation Guidelines

### For Claude Processing

**DO:**
- Convert ALL Sanskrit to IAST
- Tag every Sanskrit term with `@[...]`
- Use `@:...:@` for Sanskrit blocks
- Replace `=` with `→` in transformations
- Standardize citations to `@cite{Work:Ref}`
- Number footnotes with `[^n]`
- Add metadata tags to structural elements
- Remove horizontal rules (`---`)
- Expand or tag ditto marks

**DON'T:**
- Change Victorian-era English phrasing
- Modernize technical terminology
- Simplify complex explanations
- Remove pedagogical examples
- Alter Sanskrit content

### Quality Checklist

For each section, verify:
- ✅ All Sanskrit in IAST with proper diacritics
- ✅ All Sanskrit terms tagged `@[...]`
- ✅ Examples use `→` notation
- ✅ Citations standardized `@cite{...}`
- ✅ Cross-refs standardized `§X.Y`
- ✅ Footnotes numbered `[^n]`
- ✅ Tables have `@declension{...}` or `@table{...}` metadata
- ✅ No OCR errors (double spaces, broken words)
- ✅ No horizontal rules (`---`)
- ✅ Heading hierarchy preserved

---

## 12. Versioning

- **v7**: Current cleaned version (Tesseract OCR + standardization)
- **v8**: AST-ready version (this specification)
- **Future**: Parsed AST in JSON/database

---

## Appendix: Quick Reference

### Sanskrit Markup
```markdown
@[inline]              # Inline Sanskrit
@: block :@            # Block Sanskrit
@line: numbered :@     # Numbered block
#[English]#            # English in Sanskrit block
```

### Structure
```markdown
@chapter{...}          # Chapter
@section{...}          # Section
@rule{...}             # Grammar rule
@declension{...}       # Noun paradigm
@conjugation{...}      # Verb paradigm
@table{...}            # Generic table
```

### Examples & Relations
```markdown
@[a] + @[b] → @[c]     # Transformation
@examples{...}          # Example block
@cite{Work:Ref}        # Citation
@xref{§X.Y}            # Cross-reference
[^n]: ...              # Footnote
```

### Special
```markdown
@ditto{Case.Number}    # Ditto mark
@note{...}             # Note
@obs{...}              # Observation
@translation{...}      # Translation block
```

---

**End of Specification**
