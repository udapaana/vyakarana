# Detailed Improvements Needed

Based on comprehensive analysis of `kales_sanskrit_grammar_iast.md`

## Issues Found

### 1. **Broken Sentences: 500 instances** ⚠️ HIGH PRIORITY
**Problem:** Lines end without punctuation, breaking in mid-thought

**Examples:**
```
Line 144:  (b) Non-conjugational tenses and moods 364
Line 825: | Sing.      | Dual.          | Plural.        |            | Sing.
```

**Solution:**
- Join broken table rows
- Merge continuation lines
- Preserve intentional breaks (lists, TOC)

**Script needed:** `fix_broken_sentences.py`

### 2. **Inconsistent Spacing: 288 instances** 🔧 MEDIUM PRIORITY
**Problem:** Multiple consecutive spaces in TOC and formatting

**Examples:**
```
3 Irregular bases -  - - 65
1 Prepositions -  - - 224
```

**Solution:**
- Standardize to single space or proper markdown formatting
- Keep spacing in tables/alignments
- Convert TOC dots to proper markdown

**Script needed:** `fix_spacing.py`

### 3. **Untagged Sanskrit Words: 1,468 instances** 🏷️ HIGH PRIORITY
**Problem:** Many Sanskrit/technical terms not tagged with `@[...]`

**Examples:**
```
Determinative (should be tagged if technical term)
Benedictive (grammatical term)
Attributive (compound type)
```

**Solution:**
- Expand IAST dictionary to 200+ terms
- Tag ALL grammatical terms
- Tag compound type names
- Tag tense/mood names
- Keep common English words untagged

**Script needed:** Expand `fast_iast_converter.py`

### 4. **Footnote Formatting: 270 instances** 📝 LOW PRIORITY
**Problem:** Footnote markers not consistently formatted

**Examples:**
```
*Introduction to the 3rd Ed.
(a) A consonant except @[y], preceded
```

**Solution:**
- Use blockquotes for footnotes: `> *Note: ...`
- Consistent spacing after markers
- Group related footnotes

**Script needed:** `fix_footnotes.py`

### 5. **Abbreviations: 28 instances** 📖 LOW PRIORITY
**Problem:** Latin abbreviations could be standardized

**Examples:**
```
vide § 23  (see § 23)
e.g.       (for example)
i.e.       (that is)
viz.       (namely)
&c.        (etc.)
```

**Solution:** Keep as-is (period-appropriate) or expand for modern readers

---

## Prioritized Action Plan

### Phase 1: Critical Fixes (Est. 2-3 hours)

#### A. Expand Sanskrit Term Dictionary
**Impact:** Fixes 1,468 untagged terms

Add to `fast_iast_converter.py`:
- All compound types (Avyaya, Dvigu, etc.)
- All tense names (Aorist, Benedictive, etc.)
- All case names in Sanskrit
- All mood names
- Technical grammatical terms

```python
IAST_MAP.update({
    # Compound types
    'Dvigu': 'dvigu',
    'Avyaya': 'avyaya',

    # Tenses/moods
    'Aorist': 'aorist',
    'Benedictive': 'benedictive',
    'Conditional': 'conditional',
    'Imperative': 'imperative',
    'Optative': 'optative',

    # Cases (in context)
    'Nominative': 'nominative',  # Keep English
    'Accusative': 'accusative',
    # etc.

    # More Sanskrit terms
    'Svarita': 'svarita',
    'Udatta': 'udātta',
    'Anudatta': 'anudātta',
    # ... 100+ more
})
```

#### B. Fix Broken Tables
**Impact:** Fixes ~200 of the 500 broken sentences

Tables are splitting across lines. Need to:
1. Detect table rows (lines with `|`)
2. Join consecutive table rows
3. Preserve table structure

```python
def fix_tables(lines):
    result = []
    in_table = False
    current_row = ""

    for line in lines:
        if '|' in line and not line.startswith('#'):
            if in_table:
                current_row += line.strip()
            else:
                in_table = True
                current_row = line
        else:
            if in_table and current_row:
                result.append(current_row)
                current_row = ""
                in_table = False
            result.append(line)

    return result
```

#### C. Join True Broken Sentences
**Impact:** Fixes ~300 broken sentences

Criteria for joining:
- Line doesn't end with punctuation
- Next line continues the thought
- Not a heading, list item, or table
- Line is substantial (> 40 chars)

```python
def should_join(line1, line2):
    # Don't join if line1 ends with punctuation
    if re.search(r'[.,:;?!—…)\]]$', line1.strip()):
        return False

    # Don't join if next line is special
    if line2.startswith(('#', '-', '|', '>', '```')):
        return False

    # Don't join if in TOC (has dots + numbers)
    if re.search(r'\.\.\.\s*\d+\s*$', line1):
        return False

    # Join if substantial and flows
    return len(line1.strip()) > 40 and line2.strip()
```

### Phase 2: Polish (Est. 1-2 hours)

#### D. Fix Spacing Issues
**Impact:** Fixes 288 spacing inconsistencies

TOC spacing `- - -` → single dash `–` or proper formatting

```python
def fix_toc_spacing(line):
    # TOC lines with multiple dashes
    if re.match(r'^[^|]*\s+-\s+-\s+-\s+\d+', line):
        # Convert "Item - - - 123" to "Item – 123"
        return re.sub(r'\s+-\s+-\s+-\s+(\d+)', r' – \1', line)
    return line
```

#### E. Standardize Footnotes
**Impact:** Better readability

Use blockquote format:
```markdown
> *Note: The alphabet, it will be seen, is divided into 14 sections by Pāṇini...
```

### Phase 3: Enhancement (Est. 2-3 hours)

#### F. Convert Tables to Proper Markdown

Current:
```
| N.         | @[rāmaḥ]   | @[rāmau]       | @[rāmāḥ]       | N.         | @[jñā
| V.         | @[rāma]    | ,,             | ,,             | V.         | @[jñā
```

Should be:
```markdown
| Case | Singular | Dual | Plural |
|------|----------|------|---------|
| N.   | @[rāmaḥ] | @[rāmau] | @[rāmāḥ] |
| V.   | @[rāma]  | @[rāmau] | @[rāmāḥ] |
```

#### G. Add Blockquotes for Pāṇini Sūtras

Current:
```
@[paraḥ sannikarṣaḥ saṃhitā] | Pāṇ. 1. 4. 109.
```

Better:
```markdown
> @[paraḥ sannikarṣaḥ saṃhitā] | Pāṇ. 1. 4. 109.
```

#### H. Use Code Blocks for Paradigms

Current:
```
@[rāma] m. Rama. @[jñāna] n. knowledge.
```

Better:
```markdown
**Declension Examples:**
- `@[rāma]` (m.) – Rama
- `@[jñāna]` (n.) – knowledge
```

---

## Implementation Scripts Needed

### 1. `comprehensive_improver.py` (MAIN SCRIPT)
Combines all improvements:
- Expands IAST dictionary
- Fixes broken sentences
- Fixes spacing
- Fixes tables
- Tags Sanskrit terms

### 2. `validate_improvements.py`
Quality assurance:
- Count remaining issues
- Check for new problems
- Generate diff report

---

## Expected Results

### Before (Current):
- Broken sentences: 500
- Spacing issues: 288
- Untagged Sanskrit: 1,468
- Quality: 85%

### After (Target):
- Broken sentences: <50 (intentional only)
- Spacing issues: 0
- Untagged Sanskrit: <100 (rare terms only)
- Quality: 95%+

---

## Quick Wins (30 minutes)

1. **Expand IAST dictionary** with 100 common terms → Fixes 1000+ instances
2. **Fix obvious broken tables** → Fixes 200 instances
3. **Standardize TOC spacing** → Fixes 150 instances

**Total impact:** ~1,350 improvements in 30 minutes!

---

## Sample Improved Output

### Before:
```
(b) Non-conjugational tenses and moods 364
The Aorist is formed from the root. When Rama
said to Krishna "Oh Lord, the Sandhi rules
```

### After:
```
(b) Non-conjugational tenses and moods – 364

The @[aorist] is formed from the root. When Rāma said to Kṛṣṇa, "Oh Lord, the @[sandhi] rules..."
```

---

## Next Steps

1. Create `comprehensive_improver.py`
2. Run on full book
3. Review sample output
4. Commit improvements
5. Generate final quality report

**Estimated total time:** 5-8 hours for 95%+ quality
