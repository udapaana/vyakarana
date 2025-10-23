# Markdown Formatting Specification for Kale's Sanskrit Grammar

## File Structure

Each rule file should follow this structure:

### 1. YAML Front Matter (Required)

```yaml
---
rule: §N
---
```

### 2. Rule Content

**IMPORTANT**: Remove any rule number headers (like `#### § N.`) from the content - the rule number is already in the YAML front matter and should not be duplicated in the content.

The content should be preserved exactly as it appears in the source, with only:

- OCR errors fixed
- Formatting cleaned up
- Rule number headers removed

## Formatting Standards

### Sanskrit Notation

**Two distinct notations:**

1. **IAST (International Alphabet of Sanskrit Transliteration)**
   - Wrap in `@[...]` markers: `@[saṃskṛta]`, `@[devanāgarī]`
   - Use proper IAST diacriticals:
     - ā, ī, ū (long vowels)
     - ṛ, ṝ, ḷ, ḹ (vocalic r, l)
     - ṃ (anusvāra), ḥ (visarga)
     - ś, ṣ, ñ, ṇ, ṅ (special consonants)
     - ṭ, ḍ (retroflex)
   - Use standard capitalization (capital at sentence start, proper nouns)
   - **Do NOT convert everything to lowercase**

2. **Devanagari Script**
   - Wrap in `@deva[...]` markers: `@deva[देवनागरी]`, `@deva[संस्कृत]`
   - Ensure proper Unicode encoding
   - Keep Devanagari text accurate and unchanged

### Lists

Use proper markdown list syntax:

```markdown
- Item one
- Item two
  - Nested item

1. Numbered item
2. Numbered item
```

### Tables

Use markdown table format where tables appear:

```markdown
| Column 1 | Column 2 |
| -------- | -------- |
| Data     | Data     |
```

### Emphasis and Formatting

- **Bold**: `**text**` for strong emphasis
- _Italic_: `*text*` for emphasis
- `Code`: Backticks for technical terms or references

### Footnotes and References

- Use superscript or footnote markers
- Maintain Pāṇini references like: `Pāṇ. VI. 1. 89`
- Keep abbreviated references: `Sid. Kau.`, `Tat. B.`, `Kir.`, etc.

### Spacing

- Blank line before and after headers
- Blank line between paragraphs
- Blank line before and after lists/tables

### Examples and Notes

- Parenthetical notes: `(a)`, `(b)`, `(c)`
- Observations: `Obs.—`
- Exceptions: `Exceptions:—`
- N.B. (nota bene): `N. B.—`

## Common OCR Errors to Fix

1. **Digit confusion**: 0 vs ० (Devanagari zero), 1 vs १
2. **Character misreading**: l vs I vs 1, O vs 0
3. **Diacritical marks**: Missing or misplaced ā, ī, ś, ṣ, etc.
4. **Spacing**: Extra or missing spaces
5. **Punctuation**: Correct placement of commas, periods, colons
6. **Quote marks**: Standardize to ' ' for single quotes, " " for double quotes

## Quality Standards

- No content should be removed or changed in meaning
- All examples must be preserved
- Sanskrit terms must maintain accuracy
- References must be intact
- Grammar and spelling must be correct

## Example of Well-Formatted Rule

```markdown
---
rule: §18
---

By @[sandhi] (from @[sam] together, and @[dhā] to join) is meant the coalescence of two letters coming in immediate contact with each other.

(a) @[Saṃhitā] or @[sandhi] is necessary in the case of the internal structure of a @[pada], prepositions and roots joined together and a compound word (@[samāsa]), while in that of a sentence, i.e. in the case of the finals and initials of the different words in a sentence, it depends on the will of the writer.
```

**With Devanagari:**

```markdown
---
rule: §100
---

The @deva[अ] of root-nouns ending in @deva[वाह्] is changed to @deva[ओ] before the vowel terminations beginning with the Acc. s.; e.g. @[viśvavāh] m. the sustainer of the universe, a lord.
```

**Important Notes:**

- Rule number is in YAML front matter only - NOT repeated in content
- IAST uses `@[...]`
- Devanagari uses `@deva[...]`
