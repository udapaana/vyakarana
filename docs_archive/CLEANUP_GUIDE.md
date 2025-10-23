---
layout: "../../../layouts/BlogPostLayout.astro"
title: "Kale's Higher Sanskrit Grammar - Cleanup & Formatting Guide"
tags:
  - documentation
  - sanskrit
  - grammar
  - kale
date: 2025-10-22
draft: true
---

# Kale's Higher Sanskrit Grammar - Cleanup & Formatting Guide

## Purpose

This document tracks patterns, issues, and best practices discovered while digitizing and cleaning up chapters from Kale's "A Higher Sanskrit Grammar" (1931).

## Common OCR Issues to Watch For

### 1. Diacritical Marks

- **Issue**: OCR often misreads or drops diacritical marks
- **Common errors**:
  - ā, ī, ū, ṛ, ṝ, ḷ (long vowels)
  - ṃ (anusvāra), ḥ (visarga)
  - ñ, ṭ, ḍ, ṇ (palatals/cerebrals)
  - ś, ṣ (sibilants)
- **Fix**: Manually verify all Sanskrit terms against source

### 2. Incomplete Footnotes/Sidenotes

- **Issue**: Long footnotes get cut off mid-sentence
- **Example**: "Since short vowels include the long and the protracted vowels (See § 3, a.) another @it[इत्] '@[त्]' is generally employed to mark a" [ends abruptly]
- **Fix**: Check source PDF for complete text

### 3. Sanskrit in Mixed Contexts

- **Issue**: Sanskrit appears in various contexts requiring different formatting
- **Watch for**:
  - Inline Sanskrit: `@[devanagari]` or `@[transliteration]`
  - Block Sanskrit: `@: multi-line :@`
  - Line-numbered blocks: `@line: text :@`
  - Special markers: `@it[ṇ]`, `@marker[content]`

## Syntax Rules (CRITICAL)

### ✅ CORRECT Usage

1. **Inline Sanskrit**: Use `@[...]` for Sanskrit words/phrases in English text

   ```markdown
   The vowels @[अ], @[इ], @[उ] are called @[ह्रस्व] or short.
   ```

2. **Block Sanskrit**: Use `@: ... :@` for multi-line Sanskrit passages

   ```markdown
   @:
   अकुहविसर्जनीयानां कण्ठः ।
   इचुयशानां तालु ।
   :@
   ```

3. **English escapes in Sanskrit blocks**: Use `#[...]#` ONLY within Sanskrit contexts

   ```markdown
   @[kṛṣṇa + ūruḥ = kṛṣṇoruḥ] #[Kṛṣṇa's thigh]#
   ```

4. **Sidenotes**: Use `^{...}` for margin notes
   ```markdown
   Sanskrit is the language of the gods.^{@[संस्कृतं नाम दैवी वाक्] | Dandin.}
   ```

### ❌ INCORRECT Usage

1. **Don't use `#[e.g.]#` or `#[i.e.]#` in plain English text**
   - ❌ `#[e.g.]# @[अकार]`
   - ✅ `e.g. @[अकार]`

2. **Don't use English escape for actual Sanskrit translations**
   - Context matters: `#[...]#` is for English words WITHIN Sanskrit blocks
   - For translations of Sanskrit, use regular English after the Sanskrit

## Formatting Best Practices

### Headings Structure

```markdown
# Chapter X: Title

## I. Section Name

### § N (Paragraph number)
```

### Large Sidenotes/Footnotes

**Problem**: Long sidenotes overlap and become unreadable

**Solutions**:

1. **Short (1-2 lines)**: Keep as sidenote `^{note}`
2. **Medium (paragraph)**: Convert to blockquote
   ```markdown
   > **Note:** Extended explanation goes here...
   ```
3. **Long (multiple paragraphs)**: Create subsection

   ```markdown
   #### Note on Pāṇini's Classification

   Detailed multi-paragraph explanation...
   ```

### Tables

- Ensure proper markdown table syntax
- Tag Sanskrit content in cells: `@[sanskrit]`
- Check alignment

### Examples and Lists

- Use consistent formatting for grammar examples
- Sanskrit examples: `@[word1 + word2 = result]`
- Translations in `#[...]#` only when inline with Sanskrit

## Readability Improvements

### 1. Break Up Dense Paragraphs

- Long grammatical explanations should be split
- Use subsections for complex rules
- Add whitespace between distinct concepts
- **New**: Separate long example lists with line breaks every 2-3 examples

### 2. Highlight Important Terms

- **Bold** for key grammatical terms on first use
- Use blockquotes for important rules/exceptions

### 3. Consistent Exception Formatting

```markdown
**Exceptions:**

(a) First exception...
(b) Second exception...
```

**Always use plural "Exceptions:" even for single exception** (consistency).

### 4. Rule Citations

- Keep Pāṇini sūtra references in sidenotes: `^{@[sūtra] | Pān. X. Y. Z.}`
- Or use dedicated citation format if too many

### 5. Observation/Note Consistency

**Standardize on**:

- `**Note:**` for general notes
- `**Obs.**` for observations/remarks (preserve Kale's terminology)
- Avoid mixing `_Note:_` (italic) and `**Note:**` (bold)

## Presentation vs. Content

### Preserve (Don't Mutate)

- Original Sanskrit text
- Pāṇini sūtra references
- Technical terminology
- Example sentences
- Translations

### Enhance (Feel Free to Modify)

- Visual hierarchy (headings, spacing)
- Paragraph breaks for readability
- Sidenote → blockquote conversions
- Section organization
- Typography (bold, italic) for clarity
- Table formatting

## Chapter-Specific Patterns

### Chapter 1: The Alphabet

- Heavy use of tables for letter classifications
- Many sidenotes explaining Pāṇini's system
- Converted large Śivasūtrāṇi explanation to subsection
- **Issue found**: Incomplete footnote in § 2 about `इत्` marker

### Chapter 2: Rules of Sandhi

- Extensive rule examples: `@[a + b = c]` format
- Multiple exceptions per rule
- Dense technical content - needs paragraph breaks
- Nested rules (rules within rules) - consider hierarchical formatting
- **Issues found**:
  - Dense example lists (5+ examples without breaks)
  - Inconsistent use of "Obs." vs "Note" vs "_Note:_"
  - Nested exceptions hard to visually parse
  - Some sections need example-rule separation

## Quality Checklist

Before marking a chapter complete:

- [ ] All Sanskrit properly tagged with `@[...]`
- [ ] No `#[e.g.]#` or `#[i.e.]#` in plain English
- [ ] Incomplete footnotes identified and completed
- [ ] Large sidenotes converted to blockquotes/sections
- [ ] Diacritical marks verified
- [ ] Headings follow consistent hierarchy
- [ ] Build succeeds with no errors
- [ ] Page renders correctly in browser
- [ ] Dense paragraphs broken up for readability
- [ ] Tables properly formatted
- [ ] Examples clearly distinguished from explanatory text
- [ ] **New**: Long example lists (5+) have line breaks every 2-3 items
- [ ] **New**: Consistent use of "**Note:**" and "**Obs.**" (not mixed styles)
- [ ] **New**: Nested exceptions have clear visual hierarchy
- [ ] **New**: "Exceptions:" always plural for consistency

## Common Improvements to Make

### 1. Add Visual Breathing Room

- Blank lines between subsections
- Separate examples from rules
- Break up rule explanations

### 2. Improve Scanability

- Bold key terms
- Use blockquotes for critical rules
- Consistent formatting for exceptions
- Hierarchical headings

### 3. Enhance Navigation

- Clear section breaks
- Subsections for complex topics
- Consistent § numbering

## Git Workflow

```bash
# Commit frequently - every major change
git add src/content/posts/kale/
git commit -m "Chapter X: [specific change]"

# Examples:
git commit -m "Chapter 2: Break up dense sandhi rules for readability"
git commit -m "Chapter 2: Convert large Pāṇini footnote to subsection"
git commit -m "Chapter 2: Add blockquotes for exception rules"
```

## Risk-Taking Guidelines

**Safe to experiment with**:

- Paragraph breaks
- Heading levels (as long as hierarchy is logical)
- Sidenote → blockquote conversions
- Adding bold/italic for emphasis
- Table reformatting
- Whitespace

**Easy to revert**:

- Commit before major formatting changes
- Use git to compare: `git diff`
- Revert if needed: `git checkout -- file.md`

**The goal**: Make the grammar accessible and pleasant to read while preserving the scholarly content intact.
