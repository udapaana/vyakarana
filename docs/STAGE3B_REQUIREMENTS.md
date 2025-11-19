# Stage 3B: AI-Powered Content Cleaning & Enrichment

**Status**: 🔄 In Development  
**Date**: 2025-01-15

## Overview

Stage 3B transforms raw extracted rules (from Stage 3A) into high-quality, production-ready content using AI-powered processing. Unlike the previous failed attempt at basic automated cleaning, this stage requires intelligent AI assistance to properly understand Sanskrit grammar context and apply sophisticated markup.

## Previous Attempt - Why It Failed

**Attempted**: Basic Python automation with regex patterns  
**Result**: Poor quality output with multiple issues:

1. **Bad Titles**: 
   - "§ 50" (not descriptive)
   - "(a) Hence the consonants are given..." (entire sentence)
   
2. **No Sanskrit Markup**:
   - Plain text: "अ, तत्, एतत्" 
   - Should be: "@deva[अ], @deva[तत्], @deva[एतत्]"
   - No IAST pairing

3. **Chapter Assignment**: All marked "TBD" - no intelligent categorization

4. **Junk in Word Index**: 
   - Included punctuation: "।"
   - Single letters: "अ", "क"
   - Not meaningful technical terms

5. **No Content Structure**: 
   - No subsection headings
   - No proper formatting
   - Footnotes not converted

6. **No Cross-Reference Intelligence**: Basic regex replacement, no context understanding

**Root Cause**: Sanskrit grammar rules require linguistic understanding that simple automation cannot provide. AI is essential for quality output.

## Stage 3B Requirements

### Input
- **Source**: `/phase3_rules/core/raw/` (972 rules) and `/phase3_rules/appendix_prosody/raw/` (14 rules)
- **Format**: Markdown files with minimal YAML frontmatter from Stage 3A

### Output
- **Destination**: `/phase3_rules/core/cleaned/` and `/phase3_rules/appendix_prosody/cleaned/`
- **Format**: Fully enriched markdown with complete schema compliance

## AI Processing Tasks

### 1. Title Extraction

**Task**: Generate concise, descriptive titles (5-15 words)

**Requirements**:
- Capture the essence of the rule
- NOT the first sentence
- NOT just "§ N"
- Use grammatical terminology where appropriate

**Examples**:
- ❌ Bad: "§ 50"
- ❌ Bad: "(a) Hence the consonants are given, in the system of Pāṇini, with an अ added"
- ✅ Good: "Dropping स् in Demonstrative Pronouns"
- ✅ Good: "Consonant Naming Convention"
- ✅ Good: "Anusvāra Nasalization Rules"

### 2. Chapter Assignment

**Task**: Assign each rule to its proper chapter based on content and context

**Chapter List** (from table of contents):
1. The Alphabet (§ 1-34)
2. Euphonic Combination (Sandhi) (§ 35-72)
3. Declension of Nouns (§ 73-178)
4. Formation of Feminine Bases (§ 179-195)
5. Declension of Pronouns (§ 196-221)
6. Numerals (§ 222-241)
7. Formation of Compound Words (§ 242-303)
8. Conjugation of Verbs (§ 304-433)
9. Conjugation of Secondary Conjugations (§ 434-487)
10. Indeclinables (§ 488-500)
11. Formation of Nouns (§ 501-603)
12. Formation of Participles and Gerunds (§ 604-629)
13. Accents (§ 630-672)
14. Vedic Grammar (§ 673-807)
15. Syntax (§ 808-972)

**For Appendix**: 
- Appendix I - Prosody (all 14 rules)

**Requirements**:
- Must match exactly as shown above
- Use context clues if rule number is at chapter boundary
- For rules spanning multiple chapters, use the primary chapter

### 3. Sanskrit Markup

**Task**: Apply proper Devanagari and IAST tagging according to schema

**Format Options**:

1. **Devanagari only** (when no IAST in source):
   ```
   @deva[संस्कृत]
   ```

2. **IAST only** (when romanization only):
   ```
   @[saṃskṛta]
   ```

3. **Paired format** (when source shows both):
   ```
   @deva[संस्कृत | iast>>saṃskṛta]
   ```

**Requirements**:
- Tag ALL Devanagari text
- Tag ALL IAST romanizations
- Use paired format ONLY when source explicitly shows both
- Ensure IAST uses proper diacritics: ā, ī, ū, ṛ, ṝ, ḷ, ḹ, ṃ, ḥ, ṅ, ñ, ṭ, ḍ, ṇ, ś, ṣ
- NO ASCII approximations: H, M, sh, n, t, d, etc.

### 4. Word Index

**Task**: Extract meaningful Sanskrit technical terms for indexing

**Requirements**:
- Extract 5-20 most significant Sanskrit terms
- Must be actual technical terms, not random words
- Devanagari script preferred
- NO punctuation marks
- NO single letters unless truly significant (e.g., अ as a vowel name)
- Include grammatical terms: संस्कृत, स्वर, व्यञ्जन, स्पर्श, प्रत्याहार, सन्धि, etc.

**Examples**:
- ✅ Good: [संस्कृत, देवनागरी, स्वर, व्यञ्जन]
- ❌ Bad: [अ, ।, क, स, the]

### 5. Topic Classification

**Task**: Assign 2-10 relevant topics per rule

**Topic Categories**:
- Script/Alphabet: alphabet, devanagari, consonants, vowels
- Sandhi: sandhi, vowel-sandhi, consonant-sandhi, visarga-sandhi
- Morphology: declension, conjugation, compounds, derivation
- Noun System: masculine, feminine, neuter, cases, numbers
- Verb System: tenses, moods, voices, participles, gerunds
- Prosody: metre, syllable, pada, gana
- Grammar Terms: pratyahara, guna-vriddhi, samprasarana
- References: panini-sutra, vedic, syntax

**Requirements**:
- Be specific, not vague
- Use hyphenated format for multi-word topics
- Include both general and specific topics

### 6. Content Structuring

**Task**: Add proper markdown structure to content

**Requirements**:

1. **Main Heading**: Use `## Title` matching frontmatter title
2. **Subsections**: Use `### Subsection Name` for major divisions
3. **Lists**: Convert appropriate content to markdown lists
4. **Examples**: Use `@example[deva>>...]` or `@example[iast>>...]` tags
5. **Notes**: Convert N.B., Obs., Exception to `@note[type=X]{...}` format
6. **Cross-references**: Convert "See § N" to `@ref[N]`

**Example Structure**:
```markdown
## Dropping स् in Demonstrative Pronouns

### Before Consonants

The स् of the nominative singular of @deva[तत्] and @deva[एतत्] masculine
is dropped before a consonant...

### Examples

- @example[deva>>स शङ्कुः] - "that Shanku"
- @example[deva>>एष विष्णुः] - "this Vishnu"

### Exceptions

@note[type=exception]{The स् is NOT dropped when the word ends in क or is
used in a negative Tatpurusha compound.}

See also @ref[48] for related sandhi rules.
```

### 7. Footnote Conversion

**Task**: Convert footnote symbols to numbered references

**Requirements**:
- Convert *, †, ‡ to [^1], [^2], [^3] in order of appearance
- Place footnote content after `---` separator at end
- Format: `[^1]: Content here`
- Preserve Pāṇini sūtra references and citations

### 8. Pāṇini References

**Task**: Extract Pāṇini sūtra references from footnotes and content

**Format**: "I. 2. 29" means Aṣṭādhyāyī Book 1, Chapter 2, Sūtra 29

**Requirements**:
- Add to `panini_refs` list in frontmatter
- Format as strings: ["I. 2. 29", "I. 1. 9"]
- Extract from footnotes and inline citations

### 9. Cross-References

**Task**: Extract references to other rules in Kale's grammar

**Requirements**:
- Look for "§ N", "See § N", "§§ N-M"
- Add to `cross_refs` list in frontmatter
- Format as strings: ["§ 8", "§ 5"]
- Include both explicit and implicit references

## Complete Schema Format

```yaml
---
rule_number: 50
rule_id: "§ 50"
title: "Dropping स् in Demonstrative Pronouns"
chapter: "Declension of Pronouns"
section: "pronouns"
page_start: 40
page_end: 40
topics:
  - demonstrative-pronouns
  - declension
  - sandhi
  - nominative-case
word_index:
  - तत्
  - एतत्
  - स्
  - तत्पुरुष
panini_refs:
  - "VI. 1. 132"
cross_refs:
  - "§ 48"
  - "§ 196"
source_pages:
  - "040"
internal_pages:
  - "32"
image_files:
  - "040.png"
---

## Dropping स् in Demonstrative Pronouns

The @deva[स्] of the nominative singular of @deva[तत्] (@[tat]) and 
@deva[एतत्] (@[etat]) masculine is dropped before a consonant when they 
do not end in @deva[क] or are not used in a negative Tatpurusha compound.

### Examples

- @example[deva>>स शङ्कुः] - "that Shanku"  
- @example[deva>>एष विष्णुः] - "this Vishnu"

### Exceptions

@note[type=exception]{The @deva[स्] is NOT dropped in:}

1. When ending in @deva[क]: @example[deva>>एतत्को रुद्रः] - "this Rudra"
2. In negative Tatpurusha: @example[deva>>असौ विश्वः] - "that is not Vishnu"

### Poetic License

@note[type=observation]{In poetry, the @deva[स्] of @deva[सः] and 
@deva[एषः] may be treated as non-existent before vowels other than 
@deva[अ], allowing vowel combination for metrical requirements.}

@example[deva>>सैव मानसित्रिदुःपश्यति च ईक्षते] (Ṛg Veda II. 24. 1)

---

[^1]: Pāṇini VI. 1. 132: @deva[सकारस्य विसर्जनीयः]
```

## Processing Approach

### Option 1: Claude AI via API (Recommended)

Use Claude API to process each rule with a comprehensive prompt:

1. Read raw rule from Stage 3A
2. Send to Claude with detailed instructions
3. Parse AI response into structured format
4. Validate against schema
5. Write to cleaned directory

**Advantages**:
- High quality output
- Understands Sanskrit grammar context
- Can handle complex linguistic decisions
- Consistent results

**Code Structure**:
```python
def process_rule_with_ai(rule_num, raw_content):
    prompt = f"""
    Process this Sanskrit grammar rule following STAGE3B_REQUIREMENTS.md.
    
    Rule number: {rule_num}
    Raw content: {raw_content}
    
    Return structured YAML + markdown following the schema.
    """
    
    response = claude_api.messages.create(
        model="claude-sonnet-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return parse_and_validate(response)
```

### Option 2: Manual Processing (Fallback)

For difficult cases or quality review:
1. Open raw rule
2. Manually apply all transformations
3. Use AI assistance for Sanskrit markup
4. Validate against schema

## Quality Metrics

Each cleaned rule must pass:

1. **Schema Validation**: All required fields present and valid types
2. **Sanskrit Markup**: All Devanagari text properly tagged
3. **IAST Quality**: Proper diacritics, no ASCII approximations
4. **Title Quality**: Descriptive, concise, appropriate
5. **Chapter Accuracy**: Correct chapter assignment
6. **Word Index Quality**: Meaningful terms only, 5-20 items
7. **Topic Relevance**: 2-10 relevant topics
8. **Cross-Reference Completeness**: All § N references captured
9. **Footnote Conversion**: All footnotes properly numbered
10. **Content Structure**: Proper headings and organization

## Success Criteria

Stage 3B is complete when:
- ✅ All 972 core rules cleaned and validated
- ✅ All 14 appendix prosody rules cleaned and validated
- ✅ 100% schema compliance
- ✅ 0 validation errors
- ✅ AI quality review passed
- ✅ Ready for Stage 3C (final production polish)

## Next Stage

**Stage 3C**: Manual quality review, final refinements, and production validation.
