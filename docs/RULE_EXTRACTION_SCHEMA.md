# Rule Extraction Schema - Phase 3

## Overview

Each extracted rule follows a strict YAML + Markdown schema to ensure consistency and enable validation.

## Schema Definition

### YAML Frontmatter (Required)

```yaml
---
rule_number: 7                    # Integer: The rule number (1-972)
rule_id: "§ 7"                    # String: Display format with symbol
title: "Aspiration of Consonants" # String: Rule title/heading
chapter: "The Alphabet"           # String: Chapter name
section: "alphabet"               # String: Section slug
page_start: 13                    # Integer or String: Starting page (13, 13a, etc.)
page_end: 13                      # Integer or String: Ending page
topics:                           # Array: Keywords/topics
  - consonants
  - aspiration
  - alpa-prana
  - maha-prana
word_index:                       # Array: Key Sanskrit terms (Devanagari)
  - अल्पप्राण
  - महाप्राण
panini_refs:                      # Array: Pāṇini references (optional)
  - "I.1.9"
cross_refs:                       # Array: Cross-references (optional)
  - "§ 8"
  - "§ 5"
source_pages:                     # Array: Source page numbers
  - "013a"
---
```

### Content Structure (Required)

```markdown
## {Title}

{Main explanation text with inline markup}

### {Subsection Title} (optional)

{Subsection content}

---

[^1]: First footnote content
[^2]: Second footnote content
```

## Field Specifications

### Required Fields

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `rule_number` | Integer | 1-972 | Must match filename |
| `rule_id` | String | § N format | Must contain § |
| `title` | String | Rule heading | Non-empty |
| `chapter` | String | Chapter name | Non-empty |
| `section` | String | Section slug | Lowercase, hyphens |
| `page_start` | Integer/String | Start page | Must exist in phase2 |
| `page_end` | Integer/String | End page | >= page_start |
| `topics` | Array | Topic keywords | At least 1 |
| `word_index` | Array | Sanskrit terms | Can be empty |
| `source_pages` | Array | Source page numbers | At least 1 |

### Optional Fields

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `panini_refs` | Array | Pāṇini sutra refs | `[]` |
| `cross_refs` | Array | Related rules | `[]` |

## Content Markup Standards

### Sanskrit Terms

**CRITICAL: Use proper IAST diacritics, not ASCII approximations**

**Single Tag Format** (preferred - use when source shows only one script):
```markdown
@deva[रामः]        # Devanagari only
@[rāmaḥ]           # IAST only
```

**Paired Format** (only when source explicitly shows both scripts together):
```markdown
@deva[रामः | iast>>rāmaḥ]           # Devanagari primary, shows IAST
@[rāmaḥ | deva>>रामः]               # IAST primary, shows Devanagari
```

**Rationale**: Single tags are preferred since we have transliteration tools. Use paired format only to preserve authorial intent when the source explicitly presents both scripts together.

**Required IAST Diacritics**:
- Vowels: ā, ī, ū, ṛ, ṝ, ḷ, ḹ
- Anusvāra: ṃ (not m or n before stops)
- Visarga: ḥ (not h or :)
- Palatals: ś, c, ch, j, jh, ñ
- Retroflexes: ṭ, ṭh, ḍ, ḍh, ṇ, ṣ
- Velars: ṅ

**Common Errors to Avoid**:
```markdown
# WRONG
@[rāmaH]          # H instead of ḥ
@[rāma:]          # colon instead of ḥ
@[pitri]          # missing diacritic on ṛ
@[samskrtam]      # missing diacritics
@[sha]            # sh instead of ś

# CORRECT
@[rāmaḥ]          # proper visarga
@[pitṛ]           # vocalic r
@[saṃskṛtam]      # proper anusvāra and vocalic r
@[ś]              # proper palatal sibilant
```

### Examples

Examples use the paired format to show correspondences:

```markdown
@example[deva>>देवः | iast>>devaḥ]: the god
@example[grammatical]{stem + suffix = form}
@example[grammatical]{@deva[राम] + @deva[सु] = @deva[रामः]}
```

**Note**: Examples explicitly show both scripts for pedagogical purposes, even when single tags are preferred elsewhere in content.

### Notes

Use `@note[type=X]{content}` for inline annotations:

```markdown
@note[type=note]{Regular explanatory note}
@note[type=observation]{Observational comment (from "Obs." in source)}
@note[type=exception]{Exception to the rule}
@note[type=beginner]{Note for beginners (e.g., "may be omitted by beginners")}
```

**What goes in notes vs footnotes:**
- **Notes**: N.B., Obs., beginner notes, clarifications, explanatory content
- **Footnotes**: Pāṇini/Vārtika citations, grammar references (see below)

### Cross-References

Use `@ref[]` for cross-references to other rules. Distinguish between core rules, appendix rules, and external references:

**Core Grammar Rules** (§ 1-972):
```markdown
See @ref[8] for classification.
Compare with @ref[5,6] and @ref[8,9,10].
According to @ref[12,13,14].
```

**Appendix - Prosody Rules** (§ 1-14 in appendix):
```markdown
See @ref[prosody:3] for meter classification.
As explained in @ref[prosody:1,2].
```

**Dhātukośa (Verb Dictionary)**:
```markdown
See @ref[dhatu:भू] for root conjugation.
Compare @ref[dhatu:गम्] and @ref[dhatu:या].
```

**External References** (Pāṇini, other grammars):
```markdown
Pāṇini states @ref[panini:VI.1.77].
Vārtika: @ref[vartika:on-VI.1.101].
```

**Format Rules**:
- Core rules: Just the number `@ref[N]`
- Appendix prosody: `@ref[prosody:N]` 
- Verb dictionary: `@ref[dhatu:root]`
- External: `@ref[source:ref]`

This prevents ambiguity when appendix rules reuse § numbers (e.g., appendix § 3 vs core § 3).

### Footnotes

**CRITICAL: What Qualifies as a Footnote**

Footnotes are ONLY for scholarly citations:
1. **Pāṇini sūtra references**: `Pāṇ. I.1.9`, `Pāṇ. VIII. 3. 58`
2. **Vārtika citations**: `Vārt.`, `Vārt. 2`
3. **Other grammar texts**: References to authoritative sources

**NOT footnotes** (use `@note[]` instead):
- N. B. (Nota Bene) annotations
- Obs. (Observation) remarks
- Beginner guidance
- Explanatory content

**Format in Markdown**:
```markdown
# In text body:
The rule applies to @deva[सम्][^1] in all positions.
Both forms are valid.[^2]

# At bottom of file (after --- separator):
---

[^1]: Pāṇ. VIII. 3. 58
[^2]: @deva[सौ वक्तव्यः | iast>>sau vaktavyaḥ] Vārt. 2 to Pāṇ. I.1.9
```

**Numbering Rules**:
- Number based on order of FIRST appearance in text body
- Use consecutive integers: [^1], [^2], [^3], etc.
- Each rule file starts numbering from [^1]
- Convert OCR symbols (*, †, ‡, ×) to numbered footnotes

### Tables

Standard markdown tables:

```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data     | Data     | Data     |
```

For complex tables with Devanagari:

```markdown
| Sanskrit | IAST | Translation |
|----------|------|-------------|
| @deva[क] | @[ka] | k sound |
| @deva[ख] | @[kha] | kh sound |
```

### Examples in Source Text

When the source text uses "e.g." for examples:

```markdown
e.g. @[rāmaḥ]: Rama (nominative)
e.g. @deva[देवः]: the god
```

The "e.g." is literal text from the source material introducing an example.

## Validation Rules

### Schema Validation

1. **YAML Validity**: Must parse as valid YAML
2. **Required Fields**: All required fields present and non-empty
3. **Type Checking**: Fields match expected types
4. **Range Checking**:
   - `rule_number` in range 1-972
   - `page_start` <= `page_end`
5. **Cross-Reference**: `source_pages` exist in phase2_cleaned/
6. **Filename Match**: `rule_{N}.md` matches `rule_number: N`

### Content Validation

1. **Heading Format**: Must start with `## {Title}`
   - Format: `## Aspiration of Consonants`
   - Title must match `title` field from frontmatter
2. **Minimum Content**: At least 100 characters of substantive content
3. **Markup Validity**: All tags properly closed
   - `@deva[...]` - brackets balanced
   - `@[...]` - brackets balanced
   - `@example[...]` - proper syntax
   - `@note[type=X]{...}` - proper syntax
4. **No Error Indicators**: No "NOT FOUND", "TBD", "ERROR" in content
5. **Footnote Consistency**:
   - All `[^N]` markers in text have matching definitions
   - All footnote definitions have corresponding markers
   - Numbering is consecutive

### Quality Checks (Warnings)

1. **Examples**: Grammar rules should typically have examples
2. **Topics**: Should have at least 2-3 relevant topic tags
3. **Word Index**: Should include key Sanskrit terms from Devanagari
4. **Cross-References**: Related rules should be linked
5. **IAST Quality**: Check for common errors (H vs ḥ, : vs ḥ, missing diacritics)

## Example: Complete Valid Rule File

```yaml
---
rule_number: 7
rule_id: "§ 7"
title: "Aspiration of Consonants"
chapter: "The Alphabet"
section: "alphabet"
page_start: "13a"
page_end: "13a"
topics:
  - consonants
  - aspiration
  - alpa-prana
  - maha-prana
  - pronunciation
word_index:
  - अल्पप्राण
  - महाप्राण
panini_refs: []
cross_refs:
  - "§ 8"
  - "§ 5"
source_pages:
  - "013a"
---

## Aspiration of Consonants

Some consonants are pronounced with a slight aspiration and are designated as @deva[अल्पप्राण] (@[alpa-prāṇa]), while others which are pronounced with a stronger aspiration are called @deva[महाप्राण] (@[mahā-prāṇa]).

The first and third letters of each class, the nasals and the semi-vowels belong to the first class; the rest belong to the second class.

| Class | Unaspirated (alpa-prāṇa) | Aspirated (mahā-prāṇa) |
|-------|--------------------------|------------------------|
| Guttural | @deva[क], @deva[ग] | @deva[ख], @deva[घ] |
| Palatal | @deva[च], @deva[ज] | @deva[छ], @deva[झ] |

@note[type=note]{For convenience, the first and third letters of each class are sometimes called "unaspirates."}

@note[type=beginner]{This section may be omitted by beginners until needed.}

See @ref[8] for the complete classification of consonants.
```

## Benefits

1. **Consistency**: All rules follow identical structure
2. **Validation**: Automated verification of completeness and correctness
3. **Searchability**: Structured fields enable rich search and filtering
4. **API-Ready**: YAML frontmatter perfect for JSON/REST APIs
5. **Quality Control**: Automated checks prevent malformed data
6. **Maintainability**: Clear schema for future updates and tooling
7. **Documentation**: Self-documenting with comprehensive metadata
8. **Interoperability**: Standard formats (YAML, Markdown) ensure tool compatibility

## Common Patterns

### Multi-page Rules

```yaml
page_start: "46a"
page_end: "47b"
source_pages:
  - "046a"
  - "046b"
  - "047a"
  - "047b"
```

### Rules with Many Examples

```yaml
topics:
  - sandhi
  - vowel-combination
  - examples
```

### Rules with Pāṇini References

```yaml
panini_refs:
  - "I.1.9"
  - "VIII.3.58"
```

Content will have footnotes:
```markdown
The rule applies to @deva[सम्][^1] in all positions.

---

[^1]: Pāṇ. VIII. 3. 58: @deva[उभयसर्जनीयप्रत्ययोः | iast>>ubhayasarjanīyapratyayoḥ]
```

## Migration from Unstructured

For converting earlier extractions to this schema:

1. Parse existing markdown content
2. Extract YAML metadata from content
3. Normalize Sanskrit markup to @deva[] and @[] tags
4. Convert footnotes to numbered format [^N]
5. Validate against schema
6. Re-export with proper structure

## Implementation

Schema validation implemented in:
- `scripts/ai/parallel_extractor.py::validate_rule_schema()`
- `scripts/ai/parallel_extractor.py::validate_extracted_content()`

Extraction prompt enforces schema in:
- System prompt defines required output format
- Examples demonstrate proper structure
- Validation rejects non-compliant output
