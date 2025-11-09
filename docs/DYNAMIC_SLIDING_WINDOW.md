# Phase 2: Dynamic Sliding Window Approach

**Date**: 2025-11-07
**Strategy**: Let AI detect last complete rule and slide window accordingly

---

## Core Insight

**Rule boundaries are natural delimiters:**
- Rule § N ends when § N+1 starts (or chapter/section ends)
- AI can easily detect these boundaries
- AI tells us "last complete rule in window"
- Use that to slide window dynamically

**Benefits:**
- No fixed overlap needed
- No rule splitting
- Works with varying rule lengths
- Handles chapter breaks naturally

---

## Algorithm

```python
window_start = 9  # First page with rules
window_size = 15  # pages per window

while window_start < 550:  # End of rules section
    window_end = window_start + window_size - 1

    # 1. Load pages from all sources
    pages = load_all_sources(window_start, window_end)

    # 2. Send to AI with special instruction
    result = process_window(pages, window_start, window_end)

    # 3. Save complete rules
    for rule in result['complete_rules']:
        save_rule(rule)

    # 4. AI tells us last complete rule
    last_complete = result['last_complete_rule']
    print(f"Window {window_start}-{window_end}: Processed up to § {last_complete}")

    # 5. Find page where next rule starts
    next_rule = last_complete + 1
    next_start_page = result['next_rule_starts_at_page']

    # 6. Slide window to next rule's start
    window_start = next_start_page
```

---

## Prompt Structure

```markdown
You are processing Kale's Sanskrit Grammar from multiple OCR sources using a sliding window approach.

<style_guide>
{full style guide}
</style_guide>

<dli_google_ocr>
--- Page 9 ---
{content}
--- Page 10 ---
{content}
...
--- Page 23 ---
{content}
</dli_google_ocr>

<dli_claude_ocr>
--- Page 9 ---
{content}
...
--- Page 23 ---
{content}
</dli_claude_ocr>

<official_1931_claude_ocr>
--- Page 17 ---
{content}
...
--- Page 31 ---
{content}
</official_1931_claude_ocr>

WINDOW INFO:
- Page range: 9-23 (DLI numbering)
- This is window starting at page 9

TASK: Extract complete rules from this window

1. **Multi-source reconciliation**
   - Compare all three sources character-by-character
   - For Devanagari: prefer Claude sources
   - For IAST: prefer Claude sources
   - Where all agree: highest confidence
   - Fix obvious OCR errors

2. **Rule boundary detection**
   - Identify all § N markers in the window
   - For each rule that STARTS in this window:
     * Check if it ENDS before window ends (next § appears or section break)
     * If yes: rule is COMPLETE, extract fully
     * If no: rule is INCOMPLETE, do not extract

   **Key principle**: A rule ends when:
   - Next § N+1 appears, OR
   - Chapter/section boundary, OR
   - End of major section

3. **Identify last complete rule**
   - Determine the LAST rule number that is fully complete in this window
   - This is critical: next window will start from the page containing the NEXT rule

4. **Extract complete rules only**
   - For each complete rule, create structured markdown with YAML
   - Include all content: body, subsections, examples, notes
   - Tag all Sanskrit properly
   - Add comprehensive metadata

5. **Output format**

```json
{
  "window_info": {
    "start_page": 9,
    "end_page": 23,
    "source": "dli_numbering"
  },

  "complete_rules": [
    {
      "rule_number": 1,
      "markdown": "---\nrule: § 1\ntitle: Sanskrit Alphabet\n...\n",
      "source_pages": {
        "dli": [9],
        "official_1931": [17]
      },
      "confidence": "high"
    },
    {
      "rule_number": 2,
      "markdown": "---\nrule: § 2\n...\n",
      "source_pages": {
        "dli": [10, 11],
        "official_1931": [18, 19]
      },
      "confidence": "high"
    },
    ...
  ],

  "last_complete_rule": 12,
  "next_rule_number": 13,
  "next_rule_starts_at_page": 20,
  "next_rule_status": "starts at page 20 but incomplete in this window",

  "summary": {
    "rules_extracted": 12,
    "rules_seen_but_incomplete": 1,
    "sources_agree_percentage": 95,
    "confidence_breakdown": {
      "high": 10,
      "medium": 2,
      "low": 0
    }
  }
}
```

CRITICAL OUTPUT REQUIREMENTS:
- `last_complete_rule`: The highest rule number that is FULLY COMPLETE
- `next_rule_starts_at_page`: Page number where § {last_complete_rule + 1} begins
- This allows the next window to start at the right place
```

---

## Example Execution

### Window 1: Pages 9-23

**Input:** Pages 9-23 from all sources

**AI Processing:**
- Finds § 1 starts at page 9, ends at page 9 (§ 2 starts) ✅ COMPLETE
- Finds § 2 starts at page 10, ends at page 11 (§ 3 starts) ✅ COMPLETE
- ...
- Finds § 12 starts at page 19, ends at page 20 (§ 13 starts) ✅ COMPLETE
- Finds § 13 starts at page 20, but doesn't end before page 23 ❌ INCOMPLETE

**Output:**
```json
{
  "complete_rules": [ /* rules 1-12 */ ],
  "last_complete_rule": 12,
  "next_rule_starts_at_page": 20
}
```

**Save:** rules/rule_001.md through rules/rule_012.md

### Window 2: Pages 20-34

**Input:** Pages 20-34 (starting where § 13 begins)

**AI Processing:**
- Finds § 13 starts at page 20, ends at page 21 (§ 14 starts) ✅ COMPLETE
- Finds § 14 starts at page 21, ends at page 22 (§ 15 starts) ✅ COMPLETE
- ...
- Finds § 25 starts at page 33, but doesn't end before page 34 ❌ INCOMPLETE

**Output:**
```json
{
  "complete_rules": [ /* rules 13-24 */ ],
  "last_complete_rule": 24,
  "next_rule_starts_at_page": 33
}
```

**Save:** rules/rule_013.md through rules/rule_024.md

### Continue Until All Rules Processed...

---

## Handling Edge Cases

### Chapter/Section Breaks

If AI encounters major break:
```json
{
  "complete_rules": [ /* rules up to break */ ],
  "last_complete_rule": 45,
  "next_section": {
    "starts_at_page": 78,
    "chapter": "Chapter II - Sandhi",
    "note": "Chapter break after § 45"
  }
}
```

### Very Long Rules

If a rule spans many pages:
```json
{
  "complete_rules": [ /* previous rules */ ],
  "last_complete_rule": 67,
  "next_rule_starts_at_page": 120,
  "note": "§ 68 is unusually long (spans pages 120-135)"
}
```

**Action:** Expand next window size if needed:
```python
if note.contains("unusually long"):
    window_size = 25  # Increase to capture long rule
```

### Appendix Boundary

When reaching appendices:
```json
{
  "complete_rules": [ /* final rules */ ],
  "last_complete_rule": 972,
  "next_section": {
    "type": "appendix",
    "starts_at_page": 543,
    "title": "Appendix I: Prosody"
  },
  "main_grammar_complete": true
}
```

---

## Processing Script

```python
#!/usr/bin/env python3
"""
Dynamic sliding window rule extraction
"""

import json
from pathlib import Path

def load_window(start_page, end_page):
    """Load pages from all sources"""
    return {
        'dli_google': load_source('phase1_ocr/google', start_page, end_page),
        'dli_claude': load_source('phase1_ocr/claude', start_page, end_page),
        'official_1931': load_source('phase1_ocr/sources/official_1931', start_page, end_page)
    }

def process_window(window_data, start_page, end_page):
    """Send window to AI and get results"""

    # Build prompt with all sources
    prompt = build_prompt(window_data, start_page, end_page)

    # Call Claude (CLI or API)
    response = claude_api.call(prompt)

    # Parse JSON response
    result = json.loads(response)

    return result

def save_rules(rules):
    """Save complete rules to files"""
    Path('rules').mkdir(exist_ok=True)

    for rule in rules:
        rule_num = rule['rule_number']
        filename = f"rules/rule_{rule_num:03d}.md"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(rule['markdown'])

        print(f"  ✓ Saved § {rule_num}")

# Main processing loop
print("Starting dynamic sliding window processing...")
print("=" * 60)

window_start = 9  # First page with grammar rules
window_size = 15  # Initial window size
rules_extracted = 0

while window_start < 550:  # Until end of rules section
    window_end = min(window_start + window_size - 1, 550)

    print(f"\nWindow: pages {window_start}-{window_end}")

    # Load and process window
    window_data = load_window(window_start, window_end)
    result = process_window(window_data, window_start, window_end)

    # Save complete rules
    save_rules(result['complete_rules'])
    rules_extracted += len(result['complete_rules'])

    # Report progress
    last_rule = result['last_complete_rule']
    print(f"  Extracted rules up to § {last_rule}")
    print(f"  Total rules so far: {rules_extracted}")
    print(f"  Next rule § {result['next_rule_number']} starts at page {result['next_rule_starts_at_page']}")

    # Slide window to next rule
    window_start = result['next_rule_starts_at_page']

    # Adjust window size if needed
    if 'note' in result and 'unusually long' in result['note']:
        window_size = 25
        print(f"  ⚠ Increased window size to {window_size} for long rule")
    else:
        window_size = 15  # Reset to default

print("\n" + "=" * 60)
print(f"Processing complete! Extracted {rules_extracted} rules.")
print("Output: rules/rule_001.md through rules/rule_972.md")
```

---

## Advantages

### 1. **Natural Boundaries**
- AI understands content structure
- No arbitrary page cutoffs
- Rules never split awkwardly

### 2. **Dynamic Adaptation**
- Window slides based on content, not fixed sizes
- Handles varying rule lengths
- Works with chapter breaks

### 3. **No Redundant Processing**
- Each rule processed exactly once
- No overlap to reconcile
- Clean, efficient

### 4. **Error Recovery**
- If window fails, easy to reprocess specific window
- Clear progress tracking (last complete rule)
- Can resume from any point

### 5. **Quality Validation**
- AI reports confidence per rule
- Can identify problematic sections
- Natural checkpoint at each window

---

## Testing Plan

### 1. Test First Window (Pages 9-23)
- Verify rule extraction quality
- Check last_complete_rule detection
- Validate next_rule_starts_at_page accuracy

### 2. Test Second Window (Starting from next_rule_starts_at_page)
- Ensure smooth continuation
- No gaps or overlaps
- Rule numbers sequential

### 3. Test Edge Case Windows
- Window with chapter break
- Window with very long rule
- Window at end of grammar section

### 4. Full Run
- Process all 972 rules
- Verify completeness
- Check for any gaps

---

## Success Criteria

✅ All rules extracted (§ 1 through § 972)
✅ No gaps in rule sequence
✅ No duplicate processing
✅ Each rule well-formed with proper YAML
✅ Sanskrit properly tagged
✅ Source attribution accurate

---

**Ready to test first window!** 🚀
