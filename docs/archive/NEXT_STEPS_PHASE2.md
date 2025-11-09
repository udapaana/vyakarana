# Phase 2: Ready to Start - Next Steps

**Date**: 2025-11-07
**Status**: 🚀 **READY TO EXECUTE**

---

## Summary: What We Decided

### Approach: Dynamic Sliding Window with Multi-Source Reconciliation

**Key Innovation:** Let AI handle everything intelligently
- AI receives pages from ALL 3 sources (Google DLI, Claude DLI, Claude Official)
- AI reconciles across sources
- AI detects rule boundaries
- AI tells us "last complete rule" → we slide window from there
- Direct output: Complete rules (not pages)

**Benefits:**
- No programmatic page matching needed
- Natural rule boundaries
- Multi-source validation
- Dynamic window sliding based on content

---

## Current Status

### ✅ Complete

1. **OCR Coverage**
   - DLI_2015: 729/729 pages (Google + Claude) ✅
   - Official_1931: 603/732 pages (Claude) ✅

2. **Documentation**
   - Phase 2 stream approach designed
   - Dynamic sliding window algorithm documented
   - Processing strategy defined

3. **Test Data**
   - First window collected: `first_window_input.txt`
   - Contains pages 9-23 from all 3 sources
   - Ready for AI processing

### ⚙️ In Progress

4. **First Window Test**
   - Need to create full prompt with style guide
   - Process first window (pages 9-23)
   - Verify AI can detect last complete rule
   - Validate rule extraction quality

---

## Immediate Next Action

### Step 1: Test First Window (NOW)

Create prompt file for first window:

```markdown
# File: test_first_window_prompt.md

You are processing Kale's Sanskrit Grammar from multiple OCR sources using a sliding window approach.

<style_guide>
[Include full content from docs/STRUCTURING_RAW_OCR.md]
</style_guide>

<dli_google_ocr>
[Include DLI Google pages 9-23 from first_window_input.txt]
</dli_google_ocr>

<dli_claude_ocr>
[Include DLI Claude pages 9-23 from first_window_input.txt]
</dli_claude_ocr>

<official_1931_claude_ocr>
[Include Official pages 17-31 from first_window_input.txt]
</official_1931_claude_ocr>

WINDOW INFO:
- Page range: 9-23 (DLI numbering)
- First window of processing

TASK: Extract complete rules from this window

[Include full task instructions from DYNAMIC_SLIDING_WINDOW.md]

OUTPUT REQUIREMENTS:
Return ONLY valid JSON with this exact structure:

{
  "window_info": {
    "start_page": 9,
    "end_page": 23
  },
  "complete_rules": [
    {
      "rule_number": 1,
      "markdown": "---\nrule: § 1\n...\n[complete markdown]",
      "source_pages": {
        "dli": [9],
        "official_1931": [17]
      },
      "confidence": "high"
    }
    // ... more rules
  ],
  "last_complete_rule": X,
  "next_rule_number": X+1,
  "next_rule_starts_at_page": Y,
  "summary": {
    "rules_extracted": N,
    "sources_agree_percentage": P
  }
}
```

### Step 2: Run First Test

```bash
# Option A: Using Claude Code (recommended - no API costs)
# Just paste the prompt and get the JSON response

# Option B: Using Claude API
cat test_first_window_prompt.md | claude --model sonnet-4 > first_window_result.json

# Option C: Using Python script
python3 scripts/process_first_window.py
```

### Step 3: Validate Results

Check the output:
1. Are rules properly extracted?
2. Is Sanskrit tagged correctly?
3. Is `last_complete_rule` accurate?
4. Does `next_rule_starts_at_page` make sense?

```bash
# Parse and save rules
python3 << 'EOF'
import json

with open('first_window_result.json') as f:
    result = json.load(f)

print(f"Extracted {len(result['complete_rules'])} rules")
print(f"Last complete: § {result['last_complete_rule']}")
print(f"Next window starts at page {result['next_rule_starts_at_page']}")

# Save rules
for rule in result['complete_rules']:
    filename = f"rules/rule_{rule['rule_number']:03d}.md"
    with open(filename, 'w') as f:
        f.write(rule['markdown'])
    print(f"Saved {filename}")
EOF
```

### Step 4: Review First Rules

Manually check first few rules:
```bash
cat rules/rule_001.md
cat rules/rule_002.md
cat rules/rule_003.md
```

Verify:
- ✅ YAML front matter valid
- ✅ Sanskrit properly tagged with @deva[] and @[]
- ✅ Content complete
- ✅ Sources reconciled well

---

## Once First Window Succeeds

### Full Processing Loop

```python
#!/usr/bin/env python3
"""
Process all rules with dynamic sliding windows
"""

window_start = 9
window_size = 15
processed_rules = 0

while window_start < 550:  # End of rules section
    window_end = min(window_start + window_size - 1, 550)

    print(f"\nProcessing window: pages {window_start}-{window_end}")

    # 1. Load window from all sources
    window_data = load_window(window_start, window_end)

    # 2. Build prompt
    prompt = build_prompt(window_data, window_start, window_end)

    # 3. Call Claude
    result = claude.process(prompt)

    # 4. Save rules
    for rule in result['complete_rules']:
        save_rule(rule)
        processed_rules += 1

    print(f"  ✓ Extracted {len(result['complete_rules'])} rules")
    print(f"  ✓ Last complete: § {result['last_complete_rule']}")
    print(f"  ✓ Total so far: {processed_rules}")

    # 5. Slide window
    window_start = result['next_rule_starts_at_page']

print(f"\n✅ Complete! Extracted {processed_rules} rules")
```

### Estimated Timeline

| Stage | Time | Notes |
|-------|------|-------|
| First window test | 30 min | Verify approach works |
| Adjust prompts if needed | 30 min | Based on test results |
| Full run (pages 9-542) | ~20-30 hours | Depends on window size/speed |
| Review & validation | 2-3 hours | Spot check rules |
| **Total** | **24-35 hours** | Mostly automated |

---

## Parallel Track: Complete Official_1931 OCR

While Phase 2 is running, complete remaining Official OCR:

```bash
# In separate terminal
nohup python3 scripts/claude_vision_ocr.py \
  --source official_1931 \
  --start-page 604 \
  --end-page 732 \
  --input-dir phase1_ocr/images/official_1931 \
  --output-dir phase1_ocr/sources/official_1931 \
  > logs/official_1931_remaining.log 2>&1 &
```

This gives us complete Official source for Phase 2 v2 (if we want to reprocess with all sources later).

---

## Deliverables

After Phase 2 completes:

```
rules/
├── rule_001.md  # § 1: Sanskrit Alphabet
├── rule_002.md  # § 2: Devanagari...
├── rule_003.md
...
├── rule_972.md  # § 972: Last rule
└── processing_log.json  # Which windows processed which rules
```

Each rule file contains:
- ✅ YAML metadata (rule number, topics, cross-refs, Pāṇini refs)
- ✅ Complete rule content reconciled from all 3 sources
- ✅ Sanskrit properly tagged (@deva[] and @[])
- ✅ Source attribution
- ✅ Confidence scores

---

## After Phase 2

### Phase 3: Appendices

Process appendices (pages 543-729) separately:
- Different structure (more tables, less prose)
- Adjusted prompts
- Output to `appendices/` directory

### Phase 4: Table of Contents & Navigation

Generate from extracted rules:
```bash
python3 scripts/generate_toc.py --rules-dir rules --output TABLE_OF_CONTENTS.md
```

---

## Questions to Resolve

Before starting, confirm:

1. **Which tool to use?**
   - Claude Code CLI (no API costs, interactive)
   - Claude API (programmable, costs ~$X)

2. **Manual or automated?**
   - Manual: Copy/paste each window, review results
   - Automated: Script runs entire pipeline

3. **Review frequency?**
   - Review after each window (slower, higher quality)
   - Review after every 10 windows
   - Review only at end

---

## Success Criteria

✅ All 972 rules extracted
✅ No gaps (rule sequence 1→972 complete)
✅ Each rule has valid YAML
✅ Sanskrit tagging ≥90%
✅ Source reconciliation confidence ≥95%
✅ Multi-source validation where available

---

**Ready to start Phase 2!** The first window test is set up and ready to go. 🚀

---

## Files Created

- `first_window_input.txt` - Test data ready
- `docs/PHASE2_STREAM_APPROACH.md` - Stream approach design
- `docs/DYNAMIC_SLIDING_WINDOW.md` - Dynamic window algorithm
- `docs/PARALLEL_PROCESSING_STRATEGY.md` - Parallel execution strategy
- `NEXT_STEPS_PHASE2.md` - This file

## Documentation

See:
- [DYNAMIC_SLIDING_WINDOW.md](docs/DYNAMIC_SLIDING_WINDOW.md) - Full algorithm
- [PHASE2_STREAM_APPROACH.md](docs/PHASE2_STREAM_APPROACH.md) - Stream design
- [START_HERE.md](START_HERE.md) - Quick start guide
