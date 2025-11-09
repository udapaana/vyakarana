# Phase 2: Stream-Based Multi-Source Reconciliation

**Date**: 2025-11-07
**Approach**: Let AI handle intelligent matching and rule construction

---

## Core Idea

Instead of programmatic page matching, **stream all available OCR sources to the AI** and let it:
1. Reconcile text across sources intelligently
2. Identify rule boundaries (where § N starts/ends)
3. Construct complete rules from page fragments
4. Output structured markdown organized by **rules** (not pages)

---

## Input Format

For each processing batch (e.g., pages 1-50), provide AI with:

```
<dli_google_ocr>
=== Page 9 ===
HIGHER
SANSKRIT GRAMMAR.
Chapter I.
THE ALPHABET.
§ 1. Sanskrit, or the refined language...

=== Page 10 ===
2 HIGHER SANSKRIT GRAMMAR.
§ 2. The Devanágari alphabet...
...
</dli_google_ocr>

<dli_claude_ocr>
=== Page 9 ===
HIGHER
SANSKRIT GRAMMAR.
Chapter I.
THE ALPHABET.
§ 1. Sanskrit, or the refined language...

=== Page 10 ===
2 HIGHER SANSKRIT GRAMMAR.
§ 2. The Devanágari alphabet...
...
</dli_claude_ocr>

<official_1931_claude_ocr>
=== Page 17 ===
HIGHER
SANSKRIT GRAMMAR.

Chapter I.

THE ALPHABET.

§ 1. Sanskrit, or the refined language...

=== Page 18 ===
2                    HIGHER SANSKRIT GRAMMAR.
§ 2. The Devanágari alphabet...
...
</official_1931_claude_ocr>
```

**Note**: Different sources may use different physical page numbers for the same content. AI figures it out.

---

## AI Task

```markdown
You are processing Kale's Sanskrit Grammar from multiple OCR sources.

<style_guide>
{full style guide from STRUCTURING_RAW_OCR.md}
</style_guide>

<dli_google_ocr>
{pages 1-50 from DLI Google OCR}
</dli_google_ocr>

<dli_claude_ocr>
{pages 1-50 from DLI Claude OCR}
</dli_claude_ocr>

<official_1931_claude_ocr>
{corresponding pages from Official_1931}
</official_1931_claude_ocr>

TASK: Process this content batch and extract complete rules

1. **Multi-source reconciliation**
   - Compare all three sources character-by-character
   - For Devanagari: prefer Claude sources
   - For IAST: prefer Claude sources
   - Where sources agree: high confidence
   - Where sources differ: use best contextual reading
   - Fix obvious OCR errors across all sources

2. **Rule boundary detection**
   - Identify where each § N rule starts
   - Identify where each rule ends (next § starts or section break)
   - Handle multi-page rules (rule continues across pages)
   - Track which source pages contributed to each rule

3. **Construct complete rules**
   - Combine fragments from multiple pages into single rule
   - Preserve all content (subsections a, b, c, examples, notes)
   - Add YAML metadata for each rule
   - Tag all Sanskrit terms properly

4. **Output format**
   For each complete rule found, output:

   ```yaml
   ---
   rule: § N
   title: [rule title if present]
   source_pages:
     dli: [9, 10]
     official_1931: [17, 18]
   chapter: [chapter name]
   section: [section]
   topics: [list]
   word_index: [Devanagari words]
   panini_refs: [citations]
   cross_refs: [internal refs]
   reconciliation_sources_used: [google_dli, claude_dli, claude_official]
   confidence: high  # high/medium/low based on source agreement
   ---

   [Complete rule content with proper markup]
   ```

5. **Handle incomplete rules**
   If a rule starts but doesn't end in this batch:
   - Mark as `incomplete: true`
   - Mark as `continues_in_next_batch: true`
   - Process continuation in next batch

OUTPUT: Return JSON array of complete rules:
```json
{
  "rules": [
    {
      "rule_number": 1,
      "markdown": "---\nrule: § 1\n...",
      "status": "complete",
      "confidence": "high"
    },
    {
      "rule_number": 2,
      "markdown": "---\nrule: § 2\n...",
      "status": "complete",
      "confidence": "medium"
    },
    ...
    {
      "rule_number": 15,
      "markdown": "---\nrule: § 15\n...",
      "status": "incomplete",
      "continues_in_next_batch": true
    }
  ],
  "summary": {
    "rules_processed": 15,
    "rules_complete": 14,
    "rules_incomplete": 1,
    "pages_used": {
      "dli": [9, 10, 11, ...],
      "official": [17, 18, 19, ...]
    }
  }
}
```
```

---

## Processing Script

```python
#!/usr/bin/env python3
"""
Phase 2: Stream-based multi-source rule extraction
"""

import json
from pathlib import Path

def load_ocr_batch(source_dir, pattern, start_page, end_page):
    """Load OCR for a page range"""
    pages = []
    for page_num in range(start_page, end_page + 1):
        # Try different page formats
        patterns = [
            f"page_{page_num:03d}.txt",
            f"{page_num:03d}.txt",
            f"{page_num}.txt"
        ]

        for pat in patterns:
            file_path = Path(source_dir) / pat
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    pages.append({
                        "page": page_num,
                        "content": content
                    })
                break

    return pages

def format_ocr_stream(pages):
    """Format pages as stream for AI"""
    stream = []
    for page in pages:
        stream.append(f"=== Page {page['page']} ===")
        stream.append(page['content'])
        stream.append("")
    return "\n".join(stream)

def process_batch(start_page, end_page, output_dir):
    """Process a batch of pages from all sources"""

    # Load from all sources
    print(f"Loading pages {start_page}-{end_page} from all sources...")

    dli_google = load_ocr_batch('phase1_ocr/google', 'page_*.txt', start_page, end_page)
    dli_claude = load_ocr_batch('phase1_ocr/claude', 'page_*.txt', start_page, end_page)
    official = load_ocr_batch('phase1_ocr/sources/official_1931', '*.txt', start_page, end_page)

    print(f"  DLI Google: {len(dli_google)} pages")
    print(f"  DLI Claude: {len(dli_claude)} pages")
    print(f"  Official:   {len(official)} pages")

    # Format as streams
    streams = {
        "dli_google": format_ocr_stream(dli_google),
        "dli_claude": format_ocr_stream(dli_claude),
        "official_1931": format_ocr_stream(official)
    }

    # Load style guide
    with open('docs/STRUCTURING_RAW_OCR.md', 'r') as f:
        style_guide = f.read()

    # Build prompt
    prompt = f"""
You are processing Kale's Sanskrit Grammar from multiple OCR sources.

<style_guide>
{style_guide}
</style_guide>

<dli_google_ocr>
{streams['dli_google']}
</dli_google_ocr>

<dli_claude_ocr>
{streams['dli_claude']}
</dli_claude_ocr>

<official_1931_claude_ocr>
{streams['official_1931']}
</official_1931_claude_ocr>

[TASK instructions as shown above]
"""

    # Call Claude CLI/API
    # result = call_claude(prompt)

    # Parse result and save rules
    # ...

    return result

# Process in batches
for batch_start in range(1, 550, 50):  # Process 50 pages at a time
    batch_end = min(batch_start + 49, 542)  # Stop at end of rules

    print(f"\nProcessing batch: pages {batch_start}-{batch_end}")
    result = process_batch(batch_start, batch_end, 'rules')

    # Save each rule as separate file
    for rule in result['rules']:
        if rule['status'] == 'complete':
            rule_file = Path('rules') / f"rule_{rule['rule_number']:03d}.md"
            with open(rule_file, 'w') as f:
                f.write(rule['markdown'])
            print(f"  Saved § {rule['rule_number']}")
```

---

## Benefits of Stream Approach

### 1. **AI Handles Complexity**
- No need for programmatic page matching
- AI naturally identifies corresponding content across sources
- AI detects rule boundaries intelligently
- AI handles page numbering differences

### 2. **Direct Rule Output**
- Skip intermediate page-based structure
- Output directly organized by rules
- No need for separate "rule extraction" phase
- Cleaner pipeline: OCR → Rules

### 3. **Better Multi-Page Rules**
- AI sees larger context (50 pages at a time)
- Can properly combine rule fragments
- Understands when rules span pages
- Natural handling of continuations

### 4. **Flexible Source Handling**
- Easy to add more sources later
- AI picks best reading from any source
- No rigid page number mapping needed
- Works even if sources have different page ranges

### 5. **Simpler Code**
- No complex page equivalency logic
- No rule number extraction and matching
- Cleaner, more maintainable
- Let AI do what it's good at

---

## Processing Strategy

### Batch Size: 50 Pages

**Why 50?**
- Large enough context for AI to understand flow
- Small enough to process in reasonable time
- Rules typically 1-3 pages, so batch captures ~20-30 rules
- Fits comfortably in Claude context window

### Handling Rule Continuations

**If rule incomplete at end of batch:**
```json
{
  "rule_number": 45,
  "status": "incomplete",
  "partial_content": "...",
  "continues_in_next_batch": true
}
```

**Next batch:**
- Include note about continuing from § 45
- AI completes the rule
- Mark as complete in next batch output

### Output Structure

```
rules/
├── rule_001.md  # § 1 complete
├── rule_002.md  # § 2 complete
├── rule_003.md  # § 3 complete
...
├── rule_972.md  # § 972 complete
└── processing_log.json  # Track which batches processed which rules
```

No intermediate page files needed!

---

## Example Output

**rules/rule_001.md:**
```yaml
---
rule: § 1
title: Sanskrit Alphabet
source_pages:
  dli_google: [9]
  dli_claude: [9]
  official_1931: [17]
chapter: The Alphabet
section: introduction
topics: [alphabet, devanagari, sanskrit-basics]
word_index: [संस्कृत, देवनागरी]
panini_refs: []
cross_refs: []
reconciliation_confidence: high
sources_agree: true
---

# § 1. Sanskrit Alphabet

Sanskrit, or the refined language, is the language of @deva[देव] @[deva] or gods, and the alphabet in which it is written is called @deva[देवनागरी] @[devanāgarī], or that employed in the cities of gods.

## (a) Etymology

@note[type=observation]: The correct name for the Sanskrit alphabet is @[daiva-nāgarī] sometimes abbreviated into @[nāgarī]. Perhaps in the word @[devanāgarī] we have a history of the times when the Aryans entered and settled in Northern India...
```

---

## Next Steps

1. ✅ Finalize prompt structure with all task instructions
2. 🚀 Test on first batch (pages 1-50)
3. ✅ Verify rule outputs are complete and accurate
4. 🔄 Process all batches (pages 1-542 in groups of 50)
5. ✅ Handle appendices separately (different structure)

---

**Ready to implement this cleaner approach!** 🚀
