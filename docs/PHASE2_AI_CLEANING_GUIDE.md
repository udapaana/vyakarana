# Phase 2: AI Page Cleaning Guide

## Goal

Clean all 718 pages to remove headers/footers, preserving only actual content with structured metadata.

## What to Remove

### Page Headers (top of page)
```
§ 76-77 ]                    DECLENSION.                    43
§ 73-75 ]                    DECLENSION                    41
§ 77 ]                    DECLENSION.                    45
```
**Pattern:** `§ N` or `§ N-M` followed by `]` then chapter name then page number

### Page Footers (bottom of page)
```
44                        SANSKRIT GRAMMAR.                    [ § 77
42                        SANSKRIT GRAMMAR                     [ § 75-76
```
**Pattern:** Page number, then "SANSKRIT GRAMMAR", then `[ §`

### Internal Page Markers
```
[Internal page: 43]
```
**Pattern:** Exactly this format at start of file

## What to Keep

### Actual Rule Starts
```
§ 77. Root nouns in ई or ऊ :M. F. N.
§ 73  Compound nouns ending with पति...
§ 75.  नदी f. a river; वधू f. a woman, a bride.
```
**Pattern:** `§ N.` or `§ N  ` (with spaces) followed by actual content/title

### Section Headers (NOT page headers)
```
        Words ending in ई and ऊ mas. and fem.
                Irregular bases :—
```
**Keep these** - they're content, not page headers

### All Content
- Tables
- Sanskrit text
- Examples
- Explanations
- Subsections (a), (b), (c)
- Observations, Notes

### Footnotes
```
* From उडुलोमन् name of a sage, + इञ् ( इ ) added अपत्ये...
† एरोकाचोऽसयोगादूमाँस्त्य । ओः हाणि Pān. VI 4. 82. 83...
```
**Keep but separate** - move to footnotes section

## AI Cleaning Prompt

```
Clean this OCR page from a Sanskrit grammar book.

REMOVE:
1. Page headers: Lines matching "§ N-M ]  CHAPTER  PAGE" pattern
2. Page footers: Lines matching "PAGE  SANSKRIT GRAMMAR  [ §" pattern
3. Internal page markers: "[Internal page: N]"

KEEP & SEPARATE:
- Footnotes (lines starting with *, †, ‡) → Move to "## Footnotes" section

PRESERVE:
- All actual rule content (§ N. Title...)
- All tables, examples, Sanskrit text
- All section headers (centered text)
- Original formatting and spacing

OUTPUT FORMAT:
---
page_number: 43
chapter: "Declension"
section: "declension"
rules_starting: ["§ 77"]
rules_continuing: ["§ 76"]
has_footnotes: true
---

[Clean content]

---

## Footnotes

[Footnotes if present]

---

INPUT PAGE:

[RAW OCR TEXT]
```

## Examples

### Example 1: Page 43

**Input:**
```
[Internal page: 43]
§ 76-77 ]                    DECLENSION.                    43

  G.     वातप्रम्यः      वातप्रम्योः           वातप्रम्याम्
  L.     वातप्रम्ये         ,,                वातप्रमीषु

Decline ( गन्ति अनेन इति ) यथी a way or horse...

§ 77. Root nouns in ई or ऊ :M. F. N.

Rule of Sandhi—(a) The ending ई or उ...

* अचि इनुधातुभूवां ज्येरिय्वव्द्वौ । Pān. VI. 4. 77.
```

**Output:**
```yaml
---
page_number: 43
chapter: "Declension"
section: "declension"
rules_starting: ["§ 77"]
rules_continuing: ["§ 76"]
has_footnotes: true
---

  G.     वातप्रम्यः      वातप्रम्योः           वातप्रम्याम्
  L.     वातप्रम्ये         ,,                वातप्रमीषु

Decline ( गन्ति अनेन इति ) यथी a way or horse...

§ 77. Root nouns in ई or ऊ :M. F. N.

Rule of Sandhi—(a) The ending ई or उ...

---

## Footnotes

* अचि इनुधातुभूवां ज्येरिय्वव्द्वौ । Pān. VI. 4. 77.
```

### Example 2: Page 41 (Multiple Rules)

**Input:**
```
[Internal page: 41]
§ 73-75 ]                    DECLENSION                    41

  I.     पत्या         पतिभ्याम्               पतिभिः
  D.     पत्ये            ,,                   पतिभ्यः

§ 73  Compound nouns ending with पति such as भूपति &c...

§ 74  Obs. ( a ) ओडुलोमि a descendant of Udūloman...

        Words ending in ई and ऊ mas. and fem.

§ 75.  नदी f. a river; वधू f. a woman, a bride.

* From उडुलोमन् name of a sage...
```

**Output:**
```yaml
---
page_number: 41
chapter: "Declension"
section: "declension"
rules_starting: ["§ 73", "§ 74", "§ 75"]
rules_continuing: ["पति"]
has_footnotes: true
---

  I.     पत्या         पतिभ्याम्               पतिभिः
  D.     पत्ये            ,,                   पतिभ्यः

§ 73  Compound nouns ending with पति such as भूपति &c...

§ 74  Obs. ( a ) ओडुलोमि a descendant of Udūloman...

        Words ending in ई and ऊ mas. and fem.

§ 75.  नदी f. a river; वधू f. a woman, a bride.

---

## Footnotes

* From उडुलोमन् name of a sage...
```

## Key Distinctions

### Page Header (REMOVE)
```
§ 77 ]                    DECLENSION.                    45
```
- Has `]` after rule number
- Has chapter name
- Has page number at end
- **No actual content after the title**

### Actual Rule (KEEP)
```
§ 77. Root nouns in ई or ऊ :M. F. N.
```
- Has `.` or `  ` after rule number (not `]`)
- Has actual title/description
- **Content continues on same or next line**

## Metadata Fields

```yaml
page_number: 43           # Physical file number
chapter: "Declension"     # From removed header
section: "declension"     # Slug version
rules_starting: ["§ 77"]  # Rules that BEGIN on this page
rules_continuing: ["§ 76"] # Rules continuing from previous
has_footnotes: true       # Footnotes present
```

## Processing Strategy

### Parallel Processing
- Process 50-100 pages per batch
- Each page is independent
- Can parallelize with multiple AI calls

### Validation
After cleaning each page:
```python
# Check no headers remain
assert "SANSKRIT GRAMMAR" not in content
assert "[Internal page:" not in content

# Check YAML parses
yaml.safe_load(frontmatter)

# Check content exists
assert len(content.strip()) > 100

# Check footnotes separated if present
if has_footnotes:
    assert "## Footnotes" in output
```

### Output Structure
```
phase2_cleaned/
  page_001.md
  page_002.md
  ...
  page_718.md
```

## Next Steps After Phase 2

Once all 718 pages are cleaned:

1. **Concatenate** all cleaned pages (simple script)
   ```bash
   cat phase2_cleaned/page_*.md > phase2_master/complete_grammar.md
   ```

2. **Extract rules** by finding `§ N.` to `§ N+1.`
   - No headers to confuse extraction
   - Clean boundaries
   - Natural overlap (includes start of next rule)

3. **Validate** we got all 972 rules
   ```bash
   grep -o "§ [0-9]*\." complete_grammar.md | wc -l
   # Should be 972
   ```

## Benefits of This Approach

✅ **Clean once, use forever** - Headers removed permanently
✅ **Parallelizable** - Process 100 pages simultaneously
✅ **Reviewable** - Easy to spot-check individual pages
✅ **Fixable** - Re-clean individual pages if needed
✅ **Simple extraction** - No complex pattern matching needed
✅ **Metadata rich** - Know what's on each page

## Estimated Time

- **AI cleaning:** 718 pages ÷ 50 pages/batch = ~15 batches
- **Per batch:** ~2 minutes
- **Total cleaning time:** ~30 minutes
- **Concatenation:** ~1 minute
- **Extraction:** ~30 minutes
- **Total:** ~1 hour for complete Phase 2-3

---

Ready to process all 718 pages!
