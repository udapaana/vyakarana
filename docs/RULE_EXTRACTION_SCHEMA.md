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
examples_count: 0                 # Integer: Number of examples
has_table: false                  # Boolean: Contains tables
has_footnotes: false              # Boolean: Contains footnotes
source_pages:                     # Array: Source page files
  - "page_013a.md"
---
```

### Content Structure (Required)

```markdown
## § {N}. {Title}

{Main explanation text}

### {Subsection Title} (optional)

{Subsection content}

**Obs.**— {Observational note}

**Exception:** {Exception to the rule}

**N. B.** {Nota bene}

e.g. @deva[देवनागरी] @[IAST]: {Translation/explanation}

Footnote markers in text: [^1], [^2], etc.

At bottom of file:

[^1]: @deva[देवनागरी] @[IAST] Pāṇ. reference or citation
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
| `source_pages` | Array | Source files | At least 1, must exist |

### Optional Fields

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `panini_refs` | Array | Pāṇini sutra refs | `[]` |
| `cross_refs` | Array | Related rules | `[]` |
| `examples_count` | Integer | Example count | `0` |
| `has_table` | Boolean | Contains table | `false` |
| `has_footnotes` | Boolean | Contains footnotes | `false` |

### Derived Fields (Auto-calculated)

These fields should be calculated from content:
- `examples_count`: Count of `@example[]` tags
- `has_table`: Presence of markdown tables or `@table:`
- `has_footnotes`: Presence of `@footnote[]` tags

## Content Markup Standards

### Sanskrit Terms

**CRITICAL: Visarga must use ḥ not colon**

```markdown
@deva[देवनागरी] @[IAST]

# Correct:
@deva[रामः] @[rāmaḥ]   # Use ḥ for visarga
@deva[पितृ] @[pitṛ]     # Use ṛ for vocalic r
@deva[संस्कृतम्] @[saṃskṛtam]  # Use ṃ for anusvāra

# Incorrect:
@deva[रामः] @[rāmaH]   # Wrong: H instead of ḥ
@deva[रामः] @[rāma:]   # Wrong: colon instead of ḥ
@deva[पितृ] @[pitri]    # Wrong: missing diacritic
```

**Required IAST Diacritics**:
- Vowels: ā, ī, ū, ṛ, ṝ, ḷ, ḹ, ē, ō (though last two rare)
- Anusvāra: ṃ (not m)
- Visarga: ḥ (not h or :)
- Palatals: ś (not sh), palatal sibilant
- Retroflexes: ṭ, ṭh, ḍ, ḍh, ṇ, ṣ
- Nasals: ñ, ṅ

**Tagging Rules**:
- Always pair Devanagari with IAST: `@deva[X] @[Y]`
- Never use Devanagari alone without IAST
- Never use IAST alone without Devanagari for Sanskrit terms

### Examples
```markdown
@example[sanskrit]{देवः} @[devaḥ]: the god
@example[grammatical]{stem + suffix = form}
```

### Notes
```markdown
@note[type=note]: Regular note
@note[type=observation]: Observational note  
@note[type=exception]: Exception to the rule
```

### Cross-References
```markdown
See @ref[§ 8] for classification.
Compare with @ref[§ 5-6].
```

### Footnotes

**CRITICAL: What Qualifies as a Footnote**

Footnotes in Sanskrit grammar texts are ONLY for:
1. **Pāṇini sūtra references**: Citations to original Pāṇini grammar rules
2. **Vārtika citations**: Supplementary rules by Kātyāyana
3. **Technical grammar citations**: References to other authoritative grammar texts

**NOT footnotes** (these go in main content):
- **N. B.** notes (Nota Bene) - these are content annotations
- **Obs.** notes (Observations) - these are content observations
- Beginner notes like "Section may be omitted by beginners"
- Explanatory content or examples
- Subsection content

**Format Requirements**:
```markdown
# In text: Use [^N] where footnote marker appears
The rule applies to @deva[सम्] @[sam];[^1] examples follow.

# At bottom of file after --- separator:
---
[^1]: @deva[Sanskrit] @[IAST] Pāṇ. VIII. 3. 58
[^2]: @deva[Sanskrit] @[IAST] Vārt.
```

**Numbering Rules**:
- Number footnotes based on order of FIRST appearance in text
- Do NOT number based on order they appear at bottom of OCR
- Use consecutive numbers: [^1], [^2], [^3], etc.
- Each rule file starts numbering from [^1]

**Common Patterns from OCR**:
Original OCR may have symbols: *, †, ‡, ×, §, ¶
- Convert to [^1], [^2], [^3], etc. based on text order
- Symbol in text after word (e.g., "word*;") → [^N] in text
- Symbol at bottom (e.g., "* Pāṇ. VIII...") → [^N]: at bottom

**YAML Metadata**:
```yaml
footnotes:
  - id: 1
    content: "Pāṇ. VIII. 3. 58: @deva[उभयसर्जनीयप्रत्ययोः]"
  - id: 2
    content: "Vārt: @deva[संपुंसां सौ वक्तव्यः]"
```

### Content Notes (NOT Footnotes)

Place these directly in content as formatted text:

```markdown
**N. B.** Important note text goes here inline.

**Obs.**— Observational comment goes inline.

**Exception:** Exception text goes inline.

**Beginners may omit this section.**
```

### Tables
```markdown
| Column 1 | Column 2 |
|----------|----------|
| Data     | Data     |
```

## Validation Rules

### Schema Validation

1. **YAML Validity**: Must parse as valid YAML
2. **Required Fields**: All required fields present
3. **Type Checking**: Fields match expected types
4. **Range Checking**: `rule_number` in 1-972, pages exist
5. **Cross-Reference**: `source_pages` files exist in phase2_structured/

### Content Validation

1. **Heading Match**: Content must start with `## § {N}.`
2. **Rule Number Consistency**: Heading matches `rule_number` and `rule_id`
3. **Minimum Content**: At least 100 characters of substantive content
4. **Markup Validity**: All `@tag[]` markup properly closed
5. **No Error Messages**: No "not found", "NOT present" phrases

### Quality Checks (Warnings, not errors)

1. **Examples**: Grammar rules should have examples
2. **Topics**: Should have relevant topic tags
3. **Word Index**: Should include key terms for searchability
4. **Cross-References**: Related rules should be linked

## Example: Valid Rule File

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
examples_count: 8
has_table: true
has_footnotes: false
source_pages:
  - "page_013a.md"
---

## § 7. Aspiration of Consonants

Some consonants are pronounced with a slight aspiration and are designated as @deva[अल्पप्राण] @[Alpa-prāṇa], while others which are pronounced with a stronger aspiration are called @deva[महाप्राण] @[Mahā-prāṇa].

The first and third letters of each class, the nasals and the semi-vowels belong to the first class; the rest belong to the second class.

@note[type=note]: For the sake of convenience the first and third letters of each class are sometimes called "unaspirates."
```

## Benefits

1. **Consistency**: All rules follow identical structure
2. **Validation**: Easy to validate completeness and correctness
3. **Searchability**: Structured fields enable rich search
4. **API-Ready**: YAML frontmatter perfect for APIs
5. **Quality Control**: Automated checks prevent bad data
6. **Maintainability**: Clear schema for future updates
7. **Documentation**: Self-documenting with metadata

## Migration from Unstructured

Old extraction created freeform markdown. New schema requires:
1. Parse existing content
2. Extract metadata into YAML
3. Validate against schema
4. Re-export with proper structure

## Implementation

Schema validation implemented in:
- `scripts/ai/parallel_extractor.py::validate_rule_schema()`
- `scripts/ai/parallel_extractor.py::validate_extracted_content()`

Extraction prompt enforces schema in:
- System prompt defines required output format
- Examples demonstrate proper structure
- Validation rejects non-compliant output
