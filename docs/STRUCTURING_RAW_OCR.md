# OCR Structuring System Prompts

## Style Guide (Provided to AI in Every Request)

```markdown
# Kale's Sanskrit Grammar - Structuring Style Guide

## Core Principles

1. **Fidelity First**: Never change the content. Only add structure.
2. **Consistency**: Follow these patterns exactly across all pages.
3. **Validation**: Every change must be verifiable.

## Devanagari Markup

### Inline Devanagari

- Wrap inline Devanagari in: `@deva[संस्कृत]`
- Include spaces inside tags: `@deva[क] @deva[ख]` not `@deva[क ख]`
- Preserve original spacing around Devanagari

### Block Devanagari

- Use for multi-line Devanagari passages (tables, examples, verses)
- Format:
```

@deva:
देवनागरी लिपि
संस्कृत भाषा
:@

```
- No indentation inside block
- Blank line before and after block

## IAST Transliteration Markup

### Inline IAST
- Wrap inline IAST in: `@[saṃskṛta]`
- Use proper diacriticals: ā ī ū ṛ ṝ ḷ ḹ ṃ ḥ ś ṣ ñ ṇ ṅ ṭ ḍ
- **Always lowercase**: Sanskrit in IAST has no capitalization
  - Even at sentence start: `@[saṃskṛta]` not `@[Saṃskṛta]`
  - Even for proper nouns: `@[śiva]`, `@[rāma]`
  - Even for text names: `@[bhagavadgītā]`
- Format: `@deva[क] @[ka]` (Devanagari then IAST)
- Fix OCR capitalization errors: `@[Devanāgari]` → `@[devanāgari]`

### Block IAST
- Use for multi-line transliteration passages
- Format:
```

@:
saṃskṛtam lipi
bhāṣā śāstra
:@

````
- No indentation inside block
- Blank line before and after block

## Mixed Line Format
- Use `@line:` for lines that mix Devanagari, IAST, and English
- Common in tables, conjugation charts, declension tables
- Format: `@line: @deva[क] @[ka] k-sound :@`
- Each `@line:` must be on its own line
- Used when regular inline markup would be too cluttered

## When to Use Blocks vs Inline

**Use Inline** (`@deva[...]`, `@[...]`):
- Single words or short phrases within English text
- **Always include both** Devanagari and IAST: `@deva[राजन्] @[rājan]`
- Frontend will display only one script at a time based on user preference
- Examples scattered in paragraphs
- Definitions and glosses

**Use Line** (`@line: ... :@`):
- Table rows with mixed scripts
- Declension/conjugation paradigms
- Lists where each item has Devanagari + IAST + gloss
- **Include both** scripts in reference lists
- **May use single script** in tables (with display_preference metadata)

**Use Block** (`@deva:`, `@:`):
- Extended Devanagari passages (verses, sutras)
- Multi-line transliteration
- Block quotes in Sanskrit
- Tables with all-Devanagari content

## Subsection Markers
- Keep as-is: `(a)`, `(b)`, `(c)`, `(d)`, `(e)`
- Always on new line or after period
- Space after: `(a) Text here...`

## Special Sections

### Emphasis Markers (Standardize to @note)

Convert all varied emphasis markers to a single consistent format:

**Original markers to convert:**
- `**Obs.**—` → observation
- `**N. B.**—` → nota-bene
- `**Exception.**—` → exception
- `**Note**—` → note
- `**Remark**—` → remark

**New standardized format:**
```markdown
@note[type=nota-bene]: This is an important observation about the rule.

@note[type=exception]: When followed by a vowel, the rule changes.

@note[type=observation]: The component elements are scarcely discernible.
```

**Format rules:**
- Use `@note[type=X]:` where X is: nota-bene, observation, exception, note, remark
- Space after colon before content
- Keep on separate line or at start of paragraph
- Content follows on same line or continues on next line
- All Sanskrit in notes must be tagged: `@deva[...]` and `@[...]`

**Benefits:**
- Consistent, parseable format
- Easy to extract programmatically
- Frontend can render with custom styling per type
- Searchable by note type

### Sidenotes
- `^{...}` for Tufte-style sidenotes (very short, < 10 words)
  - Only use if won't clash with other notes
  - If multiple notes on same line: move to front matter
  - If consecutive lines would overlap: move to front matter
  - **Never omit notes** - always preserve by moving to front matter
- **Sidenotes that would clash also go in front matter**
  - Mark with `reason: "would_clash"` or `reason: "would_overlap"`

### Example Headers
- `**Examples:**` header can stay inline for example lists

## Panini References
Standardize to: `Pāṇ. [Book]. [Chapter]. [Sutra]`
- Book: Roman numerals (I, II, III, IV, V, VI, VII, VIII)
- Chapter: Arabic numerals
- Sutra: Arabic numerals
- Format: `Pāṇ. VI. 1. 89`

## Lists
- Use `-` for unordered lists (conjunct consonants, etc.)
- Use `1.` for numbered sequences
- Maintain original list structure

## YAML Front Matter Template

```yaml
---
rule: §[number]
page: [number]
chapter: [name from header]
section: [lowercase_identifier]
subsections: [a, b, c, ...]
topics: [lowercase, hyphenated, consistent]
word_index:
  - [every unique Devanagari word in content]
panini_refs:
  - [standardized references]
cross_refs:
  - [references to other rules in this grammar]
image: /images/page_[NNN].jpg
---
````

## Topic Vocabulary (Use Consistently)

- `sandhi` (not "Sandhi" or "saṃdhi")
- `alphabet` (not "letters")
- `conjuncts` (not "conjunct-consonants")
- `vowels`
- `consonants`
- `declension`
- `conjugation`
- `compounds`
- `euphonic-changes`

## Common Patterns

### Conjunct Consonant Lists

Format: `@deva[क्क] @[k-ka], @deva[क्त] @[k-ta], @deva[क्न] @[k-na]`

- Comma-separated
- Space after comma
- Maintain grouping by initial consonant

### Variant Forms

Format: `@deva[त्र], @deva[त्र] @[tra]`

- Comma between Devanagari variants
- Single IAST after all variants

### Examples with Glosses

Format: `@deva[राजन्] @[rājan] m. king`

- Devanagari, IAST, grammatical info, gloss
- Period after grammatical abbreviation

## Block Format Examples

### Example 1: Inline (scattered in text)

```markdown
The word @deva[राजन्] @[rājan] means king. It declines as @deva[राजा] @[rājā] in nominative.
```

### Example 2: Line Format (table-like structure)

```markdown
Singular forms:

@line: Nom. @deva[राजा] @[rājā] :@
@line: Acc. @deva[राजानम्] @[rājānam] :@
@line: Inst. @deva[राज्ञा] @[rājñā] :@
```

### Example 3: Devanagari Block (extended passage)

```markdown
The sutra states:

@deva:
अकः सवर्णे दीर्घः
पूर्वरूपम्
परसवर्णः
:@

This means...
```

### Example 4: IAST Block (transliteration passage)

```markdown
Transliteration:

@:
akaḥ savarṇe dīrghaḥ
pūrvarūpam
parasavarṇaḥ
:@
```

### Example 5: Mixed Content Table

```markdown
Principal conjunct consonants:

@line: @deva[क्क] @[k-ka], @deva[क्त] @[k-ta], @deva[क्न] @[k-na] :@
@line: @deva[ख्न] @[kh-na], @deva[ख्य] @[kh-ya], @deva[ख्र] @[kh-ra] :@
@line: @deva[ग्ध] @[g-dha], @deva[ग्न] @[g-na], @deva[ग्य] @[g-ya] :@
```

## What TO Change (Standardization & OCR Correction)

- ✓ IAST capitalization: **always lowercase** (Sanskrit has no capitals)
- ✓ Panini references: standardize to `Pāṇ. [Roman]. [num]. [num]`
- ✓ Topic names: use consistent vocabulary from list
- ✓ Diacriticals: ensure proper IAST diacriticals throughout
- ✓ **OCR errors**: Fix obvious scanning mistakes:
  - Spacing errors: `क् ष` → `क्ष`, `s andhi` → `sandhi`
  - Character misreading: `0` vs `o`, `1` vs `l`, `rn` vs `m`
  - Missing conjunct marks: Fix broken Devanagari ligatures
  - Garbled diacriticals: `saMskrta` → `saṃskṛta`
  - Missing words: If context clearly shows a word was skipped
  - Broken words: `conjunc-t` → `conjunct` (hyphen artifact)

## What NOT to Change (Content Alteration)

- ❌ Do not "modernize" archaic spellings (may be intentional)
- ❌ Do not change grammatical choices (even if unusual)
- ❌ Do not alter terminology or word choice
- ❌ Do not add explanatory content
- ❌ Do not reorder or restructure arguments
- ❌ Do not change examples or glosses
- ❌ Do not "improve" the author's writing

## The Distinction

**OCR Error** (FIX): `rajan` scanned as `ra1an` → correct to `rajan`
**Content** (KEEP): Author wrote `rajan` instead of `rājan` → keep as is

**OCR Error** (FIX): Missing word makes sentence incomplete → infer and add
**Content** (KEEP): Sentence is complete but unusual → keep as is

**OCR Error** (FIX): Devanagari `क्ष` scanned as two separate characters → fix ligature
**Content** (KEEP): Author uses variant spelling → keep variant

## What NOT to Change (Content Alteration)

- ❌ Do not "modernize" archaic spellings (may be intentional)
- ❌ Do not change grammatical choices (even if unusual)
- ❌ Do not alter terminology or word choice
- ❌ Do not add explanatory content
- ❌ Do not reorder or restructure arguments
- ❌ Do not change examples or glosses
- ❌ Do not "improve" the author's writing

**If uncertain whether something is OCR error or original content**: Keep as-is and flag with `[?]` for human review.

```

## Stage 1: Reconciliation Prompt

```

You are reconciling two OCR outputs of page {page_num} from Kale's Higher Sanskrit Grammar (1894).

<style_guide>
{style_guide}
</style_guide>

<claude_ocr>
{claude_ocr}
</claude_ocr>

<google_ocr>
{google_ocr}
</google_ocr>

TASK: Create a single reconciled version following these steps:

1. **Character-by-character comparison**
   - Where both agree: use that text exactly
   - Where they differ in Devanagari: prefer Claude (better with Indic scripts)
   - Where they differ in Latin text: use the more sensible reading
   - **Fix obvious OCR errors**: spacing mistakes, character misreads (0/o, 1/l, rn/m)
   - For genuinely unclear text: mark with `[?text?]`

2. **Preserve original content**
   - Every word, number, symbol must appear in output (unless OCR artifact)
   - Fix OCR spacing/scanning errors
   - Keep author's spelling choices (even if archaic)
   - Keep all punctuation (unless clearly OCR error)
   - Do not modernize or "improve" the text

3. **Output format**
   - Raw text only (no markdown yet)
   - No commentary or explanations
   - Just the reconciled page content

Output the reconciled text now:

```

## Stage 2: Structuring Prompt

```

You are structuring the OCR text into markdown with YAML front matter.

<style_guide>
{style_guide}
</style_guide>

<reconciled_text>
{reconciled_text}
</reconciled_text>

<page_context>
Page: {page_num}
Previous page ended with: {previous_context}
</page_context>

TASK: Add structure while preserving exact content.

1. **Extract metadata**
   - Rule number from content (§[N])
   - Chapter from header if present
   - All subsection markers (a, b, c, ...)
   - Topics (use consistent vocabulary from style guide)
   - Every unique Devanagari word for word_index
   - Panini references (standardize format)
   - **Extract Obs., N.B., Exceptions to front matter notes**

2. **Add markup and fix OCR errors**
   - Choose appropriate markup style:
     - Inline `@deva[...]` and `@[...]` for words in sentences
     - Line `@line: ... :@` for table rows with mixed content
     - Block `@deva:` or `@:` for multi-line passages
     - Sidenote `^{...}` for very brief marginal notes (< 10 words, one per line)
   - **Standardize IAST to all lowercase** (Sanskrit has no capitals)
   - **Fix obvious OCR errors**: spacing, character misreads, broken ligatures
   - Keep author's original content (spelling, terminology, word choice)
   - Do not add, remove, or change actual content words

3. **Output format**

   ```yaml
   ---
   [YAML front matter]
   ---
   [Content with markup]
   ```

CRITICAL RULES:
✓ Preserve every content word and meaning
✓ Fix OCR errors (spacing, character misreads, broken ligatures)
✓ Add wrapper tags @deva[...] and @[...]
✓ Use consistent topics from style guide
✗ Never alter author's actual word choices
✗ Never add explanatory text
✗ Never change sentence structure or meaning

Output the structured markdown now:

```

## Stage 3: Validation Prompt

```

You are validating that structured markdown preserves the original content.

<original>
{reconciled_text}
</original>

<structured>
{structured_markdown}
</structured>

TASK: Verify content preservation

1. **Extract content from structured version**
   - Strip YAML front matter (everything before `---` end marker)
   - Remove @deva[...] wrappers but keep content inside
   - Remove @[...] wrappers but keep content inside
   - Result should match original text

2. **Compare with standardization rules**
   - IAST capitalization changes are ALLOWED (standardization)
   - Panini reference formatting changes are ALLOWED (standardization)
   - Topic name standardization is ALLOWED (metadata only)
   - **OCR error fixes are ALLOWED**: spacing, character misreads, ligature fixes
   - Everything else must match in meaning and content

3. **Content-level comparison** (not character-by-character)
   - Flag any missing words or phrases
   - Flag any changed meanings
   - Flag any added content words (except OCR error corrections)
   - Allow spacing and formatting fixes
   - Allow corrected ligatures and diacriticals

4. **Output JSON**

```json
{
  "is_valid": true/false,
  "content_preserved_percentage": 95.5,
  "ocr_corrections_made": 12,
  "differences": [
    {
      "type": "missing|changed|added",
      "category": "ocr_fix|standardization|content_change",
      "original": "original text",
      "structured": "structured text",
      "location": "line 23, after 'conjuncts'",
      "severity": "critical|minor|acceptable"
    }
  ],
  "recommendations": [
    "Fix X by changing Y to Z"
  ]
}
```

Severity guide:

- **critical**: Content meaning changed or lost
- **minor**: Potential OCR error not fixed
- **acceptable**: Standardization or OCR correction

```

## Consistency Check Prompt (Batch)

```

You are checking consistency across {num_pages} structured pages.

<style_guide>
{style_guide}
</style_guide>

<pages>
{sample_pages}
</pages>

TASK: Identify inconsistencies and recommend standardization

1. **Check markup consistency**
   - Are all Devanagari wrapped in @deva[...]?
   - Are all IAST wrapped in @[...]?
   - Any missed words?

2. **Check metadata consistency**
   - Topics: same topic expressed different ways?
   - Section names: variations that should be unified?
   - Front matter structure: all pages follow template?

3. **Check formatting consistency**
   - Panini refs: all standardized?
   - Subsection markers: formatted consistently?
   - Lists: consistent dash/number style?

4. **Output JSON**

```json
{
  "inconsistencies": [
    {
      "type": "topic_naming",
      "variations": ["Sandhi", "sandhi", "saṃdhi"],
      "pages": [15, 18, 22],
      "recommendation": "Standardize to 'sandhi'"
    }
  ],
  "global_statistics": {
    "total_devanagari_words": 1234,
    "properly_wrapped": 1200,
    "missing_wrappers": 34
  }
}
```

````

## Key Principles

1. **Three-Stage Process**: Reconcile → Structure → Validate
2. **AI as Tool, Not Decision Maker**: Strict prompts, validation at each step
3. **Style Guide is Source of Truth**: Provided to AI in every request
4. **Human Review for Failures**: Validation failures flagged for manual check
5. **Batch Consistency**: Final pass ensures uniformity across all pages
6. **Incremental Processing**: One page at a time, with context from previous

## Stage 4: Enhancement Pass (Sanskrit Terms + Footnotes)

**Purpose**: After initial structuring, perform a focused pass to:
1. Identify and properly tag all Sanskrit terms with correct IAST
2. Standardize footnote formatting to markdown convention

**Problems Addressed**:

**Sanskrit Tagging Issues:**
- Many terms appear romanized without diacritics (e.g., "Kalidasa" instead of "Kālidāsa")
- Requires deep Sanskrit linguistic knowledge to add correct diacritics
- Work titles, author names, and technical terms may be missed in initial pass
- Front matter YAML often contains untagged Sanskrit terms

**Footnote Formatting Issues:**
- Original text uses symbols (*, †, ‡, §, ×, ¶) for footnote markers
- Need to convert to standard markdown [^1], [^2], [^3] format
- Footnote content needs proper @deva[...] and @[...] tagging
- Bottom footnotes need [^n]: format

**Solution**: Dedicated enhancement pass after all pages are initially structured.

### Stage 4 Prompt

```

You are enhancing a structured page from Kale's Sanskrit Grammar by identifying and properly tagging all Sanskrit terms.

<structured_page>
{structured_markdown}
</structured_page>

TASK 1: Standardize footnote formatting

1. **Find all footnote markers in text**
   - Symbols: *, †, ‡, §, ×, ¶, etc.
   - Convert to: [^1], [^2], [^3], [^4], [^5], [^6]
   - Number sequentially in order of appearance

2. **Convert footnote content at bottom**
   - Format: "* content" → "[^1]: content"
   - Format: "† content" → "[^2]: content"
   - Ensure Sanskrit in footnotes is tagged: @deva[...] and @[...]
   - Keep all Pāṇini references and citations

TASK 2: Identify and tag ALL Sanskrit terms with proper IAST

1. **Scan for untagged Sanskrit terms**
   - Work titles: Amarakosha, Raghuvamsa, Meghaduta, Kiratarjuniya, etc.
   - Author names: Kalidasa, Bhartrihari, Patanjali, Panini, etc.
   - Technical terms: Atmanepada, Parasmaipad, Bahuvrihi, Avyayibhava, etc.
   - Look in BOTH front matter YAML AND body content
   - Check citations, abbreviations, notes, and all metadata fields

2. **Convert to proper IAST with diacritics**
   - Amarakosha → @[amarakośa]
   - Kalidasa → @[kālidāsa]
   - Raghuvamsa → @[raghuvam̐śa]
   - Atmanepada → @[ātmanepada]
   - Parasmaipad → @[parasmaipada]
   - Bahuvrihi → @[bahuvrīhi]
   - ALL LOWERCASE (Sanskrit has no capitals)
   - Use proper diacritics: ā ī ū ṛ ṝ ḷ ḹ ṃ ḥ ś ṣ ñ ṇ ṅ ṭ ḍ

3. **Tag format**
   - In content: wrap in @[...]
   - In YAML front matter: also wrap in @[...]
   - Example in YAML: `full: "@[amarakośa]"`
   - Example in content: "the @[raghuvam̐śa] of @[kālidāsa]"

4. **Do NOT change**
   - English words (even if they sound Sanskrit-like)
   - Already properly tagged terms
   - Content structure or meaning
   - Page numbers, references, formatting

5. **Output**
   - Return the complete enhanced markdown
   - Track all changes made in a separate list

OUTPUT FORMAT:
Return ONLY a JSON object:
{{
  "enhanced_markdown": "complete markdown with all Sanskrit terms properly tagged",
  "sanskrit_terms_tagged": [
    {{"original": "Kalidasa", "enhanced": "@[kālidāsa]", "location": "front matter citation"}},
    {{"original": "Amarakosha", "enhanced": "@[amarakośa]", "location": "line 23"}}
  ],
  "terms_found": 45,
  "terms_already_tagged": 12,
  "terms_newly_tagged": 33
}}

Process the page now:

```

### Implementation Strategy

1. **After initial batch processing completes**
   - All pages have basic structure and most Sanskrit terms tagged
   - Some terms will be missing proper IAST or tags

2. **Run Stage 4 enhancement**
   - Process all structured pages through Stage 4
   - Can be done in batches or all at once
   - Lower risk since structure already exists

3. **Review enhancement results**
   - Check terms_newly_tagged count
   - Verify common terms are now consistent
   - Spot-check enhanced pages

4. **Benefits of two-pass approach**
   - Initial pass is faster, gets bulk of work done
   - Enhancement pass is focused, specialized task
   - Can refine Sanskrit term dictionary between passes
   - Lower risk of breaking existing good structure

### Common Sanskrit Terms to Tag

**Author Names:**
- @[pāṇini], @[kālidāsa], @[bhartṛhari], @[patañjali], @[kātyāyana]

**Work Titles:**
- @[amarakośa], @[raghuvam̐śa], @[meghadūta], @[kirātārjunīya]
- @[mahābhārata], @[bhāgavatapurāṇa], @[hitopadeśa]
- @[siddhāntakaumudī], @[bhāṭṭikāvya], @[śiśupālavadha]

**Grammatical Terms:**
- @[ātmanepada], @[parasmaipada], @[bahuvrīhi], @[avyayībhāva]
- @[sandhi], @[saṃhitā], @[vigraha], @[samāsa]

**Note**: This is not exhaustive - Stage 4 should identify all Sanskrit terms, not just these common ones.


# Kale's Grammar - Additional Specification Elements

## 1. Citation Registry & Standardization

### Standard Citation Formats

```yaml
citations:
  ashtadhyayi:
    format: "Pāṇ. {book}. {chapter}. {sutra}"
    link_template: "https://ashtadhyayi.com/{book}.{chapter}.{sutra}"

  siddhanta_kaumudi:
    abbreviation: "Sid. Kau."
    full_name: "Siddhānta Kaumudī"

  tattva_bodhini:
    abbreviation: "Tat. B."
    full_name: "Tattva Bodhinī"

  kiratarjuniya:
    abbreviation: "Kir."
    full_name: "Kirātārjunīya"

  # Add more as encountered
````

### In Front Matter

```yaml
citations:
  - source: ashtadhyayi
    book: VI
    chapter: 1
    sutra: 89
    context: "vowel sandhi rules"

  - source: siddhanta_kaumudi
    reference: "p. 234"
    context: "declension examples"
```

### In Content

```markdown
See Pāṇ. VI. 1. 89 for details.
```

AI should parse these and add to front matter citations array.

## 2. Abbreviation Registry

### In Style Guide

```yaml
abbreviations:
  # Gender
  m: masculine
  f: feminine
  n: neuter

  # Cases
  nom: nominative
  acc: accusative
  inst: instrumental
  dat: dative
  abl: ablative
  gen: genitive
  loc: locative
  voc: vocative

  # Numbers
  s: singular
  d: dual
  p: plural

  # Sources (see citation registry)
  Pāṇ: Pāṇini's Aṣṭādhyāyī

  # Common terms
  e.g.: for example (exempli gratia)
  i.e.: that is (id est)
  cf: compare (confer)
```

## 3. Script Display Strategy

### Reference Lists (show both)

Use when teaching script correspondences:

```markdown
@line: @deva[क्क] @[kka], @deva[क्त] @[kta], @deva[क्न] @[kna] :@
```

### Tables (show one, toggle available)

Use single script for declension/conjugation tables:

```markdown
| Case | Singular    | Dual          | Plural        |
| ---- | ----------- | ------------- | ------------- |
| Nom. | @deva[राजा] | @deva[राजानौ] | @deva[राजानः] |
```

Add display hint in front matter:

```yaml
tables:
  - id: raja_declension
    display_preference: devanagari # or iast
    toggle_available: true
```

### Running Text (both scripts, display one)

```markdown
The word @deva[राजन्] @[rājan] means king.
```

**Display Strategy:**

- Store both Devanagari and IAST in markdown
- Frontend displays only one at a time based on user preference
- Toggle switches which script is shown
- This prevents "mangling" where both scripts would switch simultaneously

**Rendering Example:**

- User preference: IAST → "The word rājan means king."
- User preference: Devanagari → "The word राजन् means king."
- Toggle keeps sentence structure intact, just swaps the script

## 4. Page Continuation Markers

```yaml
# page_015.md
continues_to: page_016
incomplete_content: true

# page_016.md
continues_from: page_015
starts_mid_content: true
```

Used for automated chapter assembly.

## 5. Variant Readings

When genuinely ambiguous:

```markdown
The form @deva[क्ष] @[kṣa]{?} is uncertain.
```

In front matter:

```yaml
uncertain_readings:
  - location: "line 23"
    text: "@deva[क्ष] @[kṣa]"
    note: "OCR unclear, possible @[kṣā]"
    confidence: "medium"
```

## 6. Example Tagging

### Inline

```markdown
E.g., @deva[राजन्] @[rājan] m. king
```

### In Front Matter

```yaml
examples:
  - devanagari: राजन्
    iast: rājan
    grammar: m
    gloss: king
    context: "declension example"
```

## 7. Cross-References

### In Content

```markdown
See §18 for details on sandhi.
```

### In Front Matter

```yaml
cross_refs:
  - rule: §18
    type: see_also
    context: "sandhi details"

  - rule: §11
    type: prerequisite

  - rule: §13
    type: continuation
```

## 8. OCR Quality Metadata

```yaml
ocr_quality:
  claude_confidence: high # high/medium/low
  google_confidence: low
  manual_review_needed: false
  devanagari_quality: high
  iast_quality: high
```

## 9. OCR Correction Tracking

### Inline (for simple corrections)

```markdown
@[rājan]{ocr: ra1an}
@deva[क्ष]{ocr: क् ष}
```

### In Front Matter (for review)

```yaml
ocr_corrections:
  - location: "line 23, subsection (c)"
    original: "ra1an"
    corrected: "rājan"
    type: "character_misread" # character_misread, spacing_error, ligature_broken, diacritical_error, missing_word
    confidence: "high" # high/medium/low
    reviewer_flag: false

  - location: "line 45"
    original: "क् ष"
    corrected: "क्ष"
    type: "spacing_error"
    confidence: "high"
    reviewer_flag: false
```

**Correction Types:**

- `character_misread`: 0→o, 1→l, rn→m
- `spacing_error`: `क् ष` → `क्ष`
- `ligature_broken`: Devanagari conjuncts separated
- `diacritical_error`: Wrong or missing diacriticals
- `missing_word`: Inferred missing word from context
- `capitalization`: IAST capitalization fixes

## 10. Observation & Note Blocks

### Standard Markers

```markdown
**Obs.**—The component elements are scarcely discernible.

**N. B.**—This rule applies universally.

**Exception.**—When followed by a vowel, the rule changes.

**Examples:**—
@line: @deva[राजा] @[rājā] nominative singular :@
```

### Long Observations (in front matter)

```yaml
notes:
  - type: observation # observation, nota_bene, exception, remark
    location: "§12c"
    content: |
      Long multiline observation that would clutter
      the front matter if included inline.
```

## 11. Figure References

```yaml
figures:
  - id: fig_12_1
    type: diagram # diagram, table, chart, illustration
    caption: "Devanagari conjunct formation"
    page: 15
    image: /images/page_015_fig1.jpg
    region: [x, y, width, height] # optional bounding box
```

## 12. Section Hierarchy

```yaml
hierarchy:
  part: 1
  part_title: "Sandhi"
  chapter: "The Alphabet"
  section: alphabet
  subsection: conjuncts
  rule: §12
```

Used for:

- Table of contents generation
- Breadcrumb navigation
- Chapter/section grouping

## 13. Related Rules

```yaml
related_rules:
  prerequisites:
    - §11 # Must understand this first

  continuations:
    - §13 # Direct continuation

  applications:
    - §45 # Where this rule is applied

  see_also:
    - §67 # Related concept

  exceptions:
    - §89 # Exception to this rule
```

## 14. Grammatical Term Glossary

Auto-built from content, but can be enriched:

```yaml
terms:
  - term_deva: संधि
    term_iast: sandhi
    definition: "coalescence of two letters"
    first_mention: §18
    related_terms: [saṃhitā]
```

## 15. Footnote Structure

```yaml
footnotes:
  - id: 1
    marker: "[^1]"
    content: "See Pāṇ. VI. 1. 89 for complete details."
    citations:
      - source: ashtadhyayi
        book: VI
        chapter: 1
        sutra: 89

  - id: 2
    marker: "[^2]"
    content: "This usage is archaic but found in classical texts."
    type: commentary # commentary, citation, clarification
```

In content:

```markdown
The rule applies here.[^1]
```

## Complete Front Matter Example

```yaml
---
rule: §12
page: 15
chapter: The Alphabet
section: alphabet
subsections: [c, d, e]
topics: [conjuncts, consonants, devanagari, variants]

hierarchy:
  part: 1
  chapter: The Alphabet
  section: alphabet
  subsection: conjuncts

word_index:
  - क्ष
  - ज्ञ
  - त्र

citations:
  - source: ashtadhyayi
    book: VI
    chapter: 1
    sutra: 89

cross_refs:
  - rule: §11
    type: prerequisite
  - rule: §13
    type: continuation

related_rules:
  prerequisites: [§11]
  continuations: [§13]

continues_to: page_016
incomplete_content: true

ocr_quality:
  claude_confidence: high
  google_confidence: low
  manual_review_needed: false

ocr_corrections:
  - location: "line 23"
    original: "ra1an"
    corrected: "rājan"
    type: "character_misread"
    confidence: "high"

examples:
  - devanagari: क्ष
    iast: kṣ
    context: "conjunct example"

footnotes:
  - id: 1
    content: "Component elements scarcely discernible"

image: /images/page_015.jpg
---
```

## AI Processing Instructions

When structuring content, the AI should:

1. **Parse all citations** and add to `citations` array
2. **Identify cross-references** (§N mentions) and add to `cross_refs`
3. **Extract all examples** with Devanagari/IAST pairs
4. **Track OCR corrections** made during structuring
5. **Flag uncertain readings** for human review
6. **Build word index** from all Devanagari in content
7. **Detect footnote markers** and structure appropriately
8. **Identify observation blocks** (Obs., N.B., Exception)
9. **Determine hierarchy** from page context
10. **Mark page continuations** when content is incomplete

"""
MCP Server for Kale's Grammar OCR Processing Pipeline

Focus: Accurate and efficient batch processing to produce clean markdown output

Tools provided:

1. list_ocr_pages - List available OCR files with processing status
2. get_page_batch - Get OCR for multiple pages at once (batch processing)
3. save_structured_page - Save processed markdown with validation
4. get_processing_status - Check progress and identify issues
5. get_consistency_data - Get accumulated consistency info for current batch
6. update_consistency_data - Update consistency tracking incrementally
7. get_validation_report - Get validation results for review
   """

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import yaml
import re

class KaleGrammarMCPServer:
"""MCP Server for efficient, accurate OCR processing"""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.ocr_claude = self.repo_path / "ocr_output" / "claude"
        self.ocr_google = self.repo_path / "ocr_output" / "google"
        self.output_dir = self.repo_path / "structured_pages"
        self.status_file = self.repo_path / "processing_status.json"
        self.consistency_file = self.repo_path / "consistency_data.json"

        # Initialize
        self.output_dir.mkdir(exist_ok=True)
        self._load_status()
        self._load_consistency_data()

    def _load_status(self):
        """Load processing status"""
        if self.status_file.exists():
            self.status = json.loads(self.status_file.read_text())
        else:
            self.status = {
                "processed_pages": [],
                "needs_review": [],
                "validation_failures": [],
                "last_updated": None,
                "total_pages": 0
            }

    def _save_status(self):
        """Save processing status"""
        self.status["last_updated"] = datetime.now().isoformat()
        self.status_file.write_text(json.dumps(self.status, indent=2))

    def _load_consistency_data(self):
        """Load global consistency tracking"""
        if self.consistency_file.exists():
            self.consistency = json.loads(self.consistency_file.read_text())
        else:
            self.consistency = {
                "terms": {},  # term -> {pages: [], devanagari: "", definition: ""}
                "citations": {},  # source -> [all citations]
                "abbreviations": {},  # abbr -> expansion
                "topics": [],  # all unique topics (stored as list)
                "devanagari_words": {}  # word -> [page numbers]
            }

    def _save_consistency_data(self):
        """Save consistency data"""
        self.consistency_file.write_text(
            json.dumps(self.consistency, indent=2, ensure_ascii=False)
        )

    # ========== MCP TOOLS ==========

    def list_ocr_pages(self) -> Dict:
        """List all available OCR page files with processing status"""
        claude_pages = sorted([
            int(f.stem.split('_')[1])
            for f in self.ocr_claude.glob("page_*.txt")
        ])
        google_pages = sorted([
            int(f.stem.split('_')[1])
            for f in self.ocr_google.glob("page_*.txt")
        ])

        # Find pages with both OCRs
        both = sorted(set(claude_pages) & set(google_pages))
        processed = [int(p.split('_')[1]) for p in self.status["processed_pages"]]
        remaining = sorted(set(both) - set(processed))

        return {
            "total_pages": len(both),
            "pages": both,
            "processed": sorted(processed),
            "processed_count": len(processed),
            "needs_review": self.status["needs_review"],
            "needs_review_count": len(self.status["needs_review"]),
            "remaining": remaining,
            "remaining_count": len(remaining),
            "completion_percentage": (len(processed) / len(both) * 100) if both else 0
        }

    def get_page_batch(self, page_nums: List[int]) -> Dict:
        """
        Get OCR for multiple pages at once for batch processing

        This is KEY for efficiency: load multiple pages in one call
        so Claude can process them in a single conversation with
        shared context and consistency data
        """
        batch_data = []

        for page_num in page_nums:
            page_name = f"page_{page_num:03d}"
            claude_file = self.ocr_claude / f"{page_name}.txt"
            google_file = self.ocr_google / f"{page_name}.txt"

            if not claude_file.exists() or not google_file.exists():
                batch_data.append({
                    "page": page_num,
                    "error": "OCR files not found"
                })
                continue

            batch_data.append({
                "page": page_num,
                "claude_ocr": claude_file.read_text(encoding='utf-8'),
                "google_ocr": google_file.read_text(encoding='utf-8'),
                "status": page_name in self.status["processed_pages"]
            })

        return {
            "batch_size": len(page_nums),
            "pages": batch_data,
            "consistency_hints": self._build_consistency_hints()
        }

    def _build_consistency_hints(self) -> Dict:
        """Build consistency hints for current batch"""
        topics = self.consistency.get("topics", [])
        terms = list(self.consistency.get("terms", {}).keys())[:20]
        citations = list(self.consistency.get("citations", {}).keys())

        return {
            "topics": topics,
            "common_terms": terms,
            "citation_sources": citations,
            "total_pages_processed": len(self.status["processed_pages"])
        }

    def save_structured_page(self, page_num: int, markdown: str,
                            validation: Dict, ocr_corrections: List[Dict]) -> Dict:
        """
        Save structured markdown with validation results

        Includes OCR corrections tracking for review and model improvement
        """
        page_name = f"page_{page_num:03d}"

        # Save markdown
        md_file = self.output_dir / f"{page_name}.md"
        md_file.write_text(markdown, encoding='utf-8')

        # Save validation report with OCR corrections
        validation_data = {
            "validation": validation,
            "ocr_corrections": ocr_corrections,
            "timestamp": datetime.now().isoformat()
        }
        validation_file = self.output_dir / f"{page_name}_validation.json"
        validation_file.write_text(
            json.dumps(validation_data, indent=2, ensure_ascii=False)
        )

        # Update status
        if page_name not in self.status["processed_pages"]:
            self.status["processed_pages"].append(page_name)

        # Track validation failures
        if not validation.get("is_valid", False):
            if page_name not in self.status["needs_review"]:
                self.status["needs_review"].append(page_name)
                self.status["validation_failures"].append({
                    "page": page_name,
                    "page_num": page_num,
                    "timestamp": datetime.now().isoformat(),
                    "issues": len(validation.get("differences", [])),
                    "severity": "critical" if validation.get("content_preserved_percentage", 100) < 95 else "minor"
                })

        self._save_status()

        return {
            "success": True,
            "page": page_num,
            "file": str(md_file),
            "needs_review": not validation.get("is_valid", False),
            "ocr_corrections_count": len(ocr_corrections)
        }

    def get_processing_status(self) -> Dict:
        """Get overall processing status and statistics"""
        all_pages = self.list_ocr_pages()

        # Calculate statistics
        needs_review_critical = [
            f for f in self.status.get("validation_failures", [])
            if f.get("severity") == "critical"
        ]

        return {
            "total_pages": all_pages["total_pages"],
            "processed": all_pages["processed_count"],
            "remaining": all_pages["remaining_count"],
            "needs_review": all_pages["needs_review_count"],
            "needs_review_critical": len(needs_review_critical),
            "completion_percentage": all_pages["completion_percentage"],
            "pages_needing_review": self.status["needs_review"],
            "critical_failures": [f["page"] for f in needs_review_critical],
            "last_updated": self.status.get("last_updated"),
            "next_batch_recommendation": self._recommend_next_batch()
        }

    def _recommend_next_batch(self, batch_size: int = 10) -> List[int]:
        """Recommend next batch of pages to process"""
        all_pages = self.list_ocr_pages()
        remaining = all_pages["remaining"]

        # Return next N pages
        return remaining[:batch_size] if remaining else []

    def get_consistency_data(self, data_type: Optional[str] = None) -> Dict:
        """
        Get global consistency data for reference during processing

        Used to ensure consistent terminology, topics, and formatting
        across all processed pages
        """
        if data_type:
            return {
                data_type: self.consistency.get(data_type, {}),
                "page_count": len(self.status["processed_pages"])
            }

        # Return summary for efficiency
        return {
            "topics": self.consistency.get("topics", []),
            "term_count": len(self.consistency.get("terms", {})),
            "top_terms": list(self.consistency.get("terms", {}).keys())[:20],
            "citation_sources": list(self.consistency.get("citations", {}).keys()),
            "devanagari_word_count": len(self.consistency.get("devanagari_words", {})),
            "pages_processed": len(self.status["processed_pages"])
        }

    def update_consistency_data(self, page_num: int, metadata: Dict) -> Dict:
        """
        Update global consistency tracking with data from processed page

        This is called after each page is processed to accumulate
        knowledge that improves consistency in subsequent pages
        """

        # Track terms
        for term in metadata.get("terms", []):
            term_key = term.get("term_iast", "")
            if not term_key:
                continue

            if term_key not in self.consistency["terms"]:
                self.consistency["terms"][term_key] = {
                    "pages": [],
                    "devanagari": term.get("term_deva"),
                    "definition": term.get("definition")
                }

            if page_num not in self.consistency["terms"][term_key]["pages"]:
                self.consistency["terms"][term_key]["pages"].append(page_num)

        # Track citations
        for citation in metadata.get("citations", []):
            source = citation.get("source")
            if not source:
                continue

            if source not in self.consistency["citations"]:
                self.consistency["citations"][source] = []

            self.consistency["citations"][source].append({
                "page": page_num,
                "reference": citation
            })

        # Track topics (maintain as list, not set)
        topics = metadata.get("topics", [])
        existing_topics = set(self.consistency["topics"])
        for topic in topics:
            if topic not in existing_topics:
                self.consistency["topics"].append(topic)
                existing_topics.add(topic)

        # Track Devanagari words
        for word in metadata.get("word_index", []):
            if word not in self.consistency["devanagari_words"]:
                self.consistency["devanagari_words"][word] = []

            if page_num not in self.consistency["devanagari_words"][word]:
                self.consistency["devanagari_words"][word].append(page_num)

        self._save_consistency_data()

        return {
            "success": True,
            "page": page_num,
            "total_terms": len(self.consistency["terms"]),
            "total_topics": len(self.consistency["topics"]),
            "total_devanagari_words": len(self.consistency["devanagari_words"])
        }

    def get_validation_report(self, page_num: Optional[int] = None) -> Dict:
        """
        Get validation report for specific page or summary of all failures

        Includes OCR corrections for review and potential model training
        """
        if page_num:
            page_name = f"page_{page_num:03d}"
            validation_file = self.output_dir / f"{page_name}_validation.json"

            if not validation_file.exists():
                return {"error": f"No validation report for page {page_num}"}

            return json.loads(validation_file.read_text())
        else:
            # Return summary of all validation failures
            failures = self.status.get("validation_failures", [])

            critical = [f for f in failures if f.get("severity") == "critical"]
            minor = [f for f in failures if f.get("severity") == "minor"]

            return {
                "total_failures": len(failures),
                "critical_failures": len(critical),
                "minor_failures": len(minor),
                "critical_pages": [f["page_num"] for f in critical],
                "minor_pages": [f["page_num"] for f in minor],
                "failures": failures
            }

    def get_page_content(self, page_num: int) -> Dict:
        """
        Get processed content for a specific page

        Useful for review or re-processing
        """
        page_name = f"page_{page_num:03d}"
        md_file = self.output_dir / f"{page_name}.md"

        if not md_file.exists():
            return {"error": f"Page {page_num} not yet processed"}

        content = md_file.read_text(encoding='utf-8')

        # Parse front matter
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
        if match:
            try:
                metadata = yaml.safe_load(match.group(1))
                body = match.group(2)
                return {
                    "page": page_num,
                    "metadata": metadata,
                    "content": body,
                    "full_markdown": content
                }
            except:
                pass

        return {
            "page": page_num,
            "full_markdown": content
        }

# MCP Server Configuration

MCP_SERVER_CONFIG = {
"name": "kale-grammar-processor",
"version": "1.0.0",
"description": "Efficient and accurate OCR processing for Kale's Sanskrit Grammar",
"goal": "Produce clean, well-structured markdown files that are AST parseable",
"tools": [
{
"name": "list_ocr_pages",
"description": "List all available OCR files with processing status",
"parameters": {}
},
{
"name": "get_page_batch",
"description": "Get OCR for multiple pages at once (batch processing)",
"parameters": {
"page_nums": {
"type": "array",
"items": {"type": "integer"},
"description": "List of page numbers to fetch (recommend 10 at a time)",
"required": True
}
}
},
{
"name": "save_structured_page",
"description": "Save processed markdown with validation and OCR corrections",
"parameters": {
"page_num": {"type": "integer", "required": True},
"markdown": {"type": "string", "required": True},
"validation": {"type": "object", "required": True},
"ocr_corrections": {
"type": "array",
"items": {"type": "object"},
"description": "List of OCR corrections made",
"required": True
}
}
},
{
"name": "get_processing_status",
"description": "Get overall processing status and next batch recommendation",
"parameters": {}
},
{
"name": "get_consistency_data",
"description": "Get accumulated consistency info (topics, terms, citations)",
"parameters": {
"data_type": {
"type": "string",
"required": False,
"enum": ["topics", "terms", "citations", "devanagari_words", "abbreviations"]
}
}
},
{
"name": "update_consistency_data",
"description": "Update consistency tracking after processing a page",
"parameters": {
"page_num": {"type": "integer", "required": True},
"metadata": {"type": "object", "required": True}
}
},
{
"name": "get_validation_report",
"description": "Get validation results (specific page or summary)",
"parameters": {
"page_num": {
"type": "integer",
"required": False,
"description": "Specific page number, or omit for summary"
}
}
},
{
"name": "get_page_content",
"description": "Get processed content for a specific page",
"parameters": {
"page_num": {"type": "integer", "required": True}
}
}
],
"workflow": {
"description": "Efficient batch processing workflow",
"steps": [
"1. Call list_ocr_pages to see what needs processing",
"2. Call get_page_batch with 10 page numbers",
"3. Process batch in single conversation (efficiency!)",
"4. For each page: reconcile → structure → validate",
"5. Call save_structured_page for each processed page",
"6. Call update_consistency_data to track terms/topics",
"7. Repeat steps 2-6 for next batch",
"8. Review validation failures with get_validation_report"
]
}
}
