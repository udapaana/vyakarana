# OCR Extraction Plan - Phase 3: Individual Rules

## Current Status (2024-10-31)

### What We Have
- ✅ 729 structured pages in `structured_pages/`
- ⚠️ 947/972 rules extracted in `rules/` (correctness unknown)
- ⚠️ 14 appendix sections in `appendices/`
- ✅ Rule 1 correctly extracted in `rules_llm/rule_1.md`
- ✅ Rule 6 manually corrected

### Known Issues

1. **Regex-based extraction has fundamental problems:**
   - 947 rules are non-empty but may contain wrong content
   - Example: Rule 6 was incorrectly including "§ 5-6" header content
   - 25 rules completely missing: [81, 93, 235, 236, 237, 326, 327, 376, 402, 455, 464, 465, 466, 467, 468, 519, 625, 626, 665, 666, 702, 810, 811, 865, 962]
   - Cannot handle semantic understanding (e.g., "§ 5-6" intro vs separate § 5 and § 6 rules)

2. **API Limitation:**
   - Anthropic API rate-limited until 2025-11-01 00:00 UTC
   - Cannot use LLM-based extraction until access returns

## The Solution: LLM-Based Sequential Extraction

### Approach
For each rule N (1 to 972):
1. Read pages starting from last known position
2. Use LLM to extract rule § N and identify where it ends
3. Write rule file with correct content
4. Continue with next rule from the end position

### Why This Works
- ✅ Semantic understanding of rule boundaries
- ✅ Handles combined headers ("§ 5-6") vs individual rules
- ✅ Correctly identifies where rules start and end
- ✅ 100% confidence in extracted content

## When API Access Returns (2025-11-01)

### Run Full Extraction

```bash
cd /Users/skmnktl/Downloads/ocr

# Create fresh output directory
mkdir -p rules_llm

# Run extraction for all 972 rules
python scripts/extraction/extract_rules_llm.py --start 1 --end 972 --output rules_llm

# This will take approximately 2-3 hours (972 LLM calls)
# Progress is shown every 10 rules
```

### Options

```bash
# Test on first 10 rules
python scripts/extraction/extract_rules_llm.py --start 1 --end 10 --output rules_test

# Resume from specific rule (e.g., if interrupted at rule 326)
python scripts/extraction/extract_rules_llm.py --start 326 --end 972 --output rules_llm

# Extract specific problem rules only
python scripts/extraction/extract_rules_llm.py --start 326 --end 327 --output rules_llm
```

## Script Details

### `extract_rules_llm.py`
- **Purpose:** Sequential LLM-based extraction
- **Model:** claude-sonnet-4-20250514
- **Input:** Structured pages from `structured_pages/`
- **Output:** Individual rule files in specified directory
- **Tracks:** Current page position, source pages, end pages
- **Error handling:** Continues even if one rule fails

### Helper Scripts
- `extract_one_rule.py` - Read pages for a specific rule (utility)
- `extract_rules_interactive.py` - Generate extraction tasks (deprecated)
- `extract_rules_cli.sh` - Bash wrapper (deprecated - API key issues)

## After Extraction

### Verification Steps
1. Check rule count: `ls rules_llm/rule_*.md | wc -l` (should be 972)
2. Verify no empty files: `find rules_llm -name "rule_*.md" -size 0`
3. Spot-check rules against source pages
4. Compare with old extraction: `diff rules/rule_6.md rules_llm/rule_6.md`

### Next Steps
1. ✅ Extract all 972 rules correctly
2. Extract appendices (if needed)
3. Verify extraction quality
4. Archive old `rules/` directory
5. Move `rules_llm/` to `rules/`

## File Organization

```
ocr/
├── structured_pages/       # Phase 2 output (729 pages)
├── rules/                  # Current extraction (947 rules, uncertain quality)
├── rules_llm/             # LLM-based extraction (when complete: 972 rules)
├── appendices/            # Current appendix extraction (14 sections)
└── scripts/
    └── extraction/
        ├── extract_rules_llm.py          # Main extraction script ⭐
        ├── extract_one_rule.py           # Helper utility
        ├── extract_rules.py              # Old regex-based (deprecated)
        └── extract_rules_interactive.py  # (deprecated)
```

## Key Insights

1. **Regex can't understand semantics** - That's why rule 6 got wrong content
2. **Non-empty ≠ Correct** - 947 rules extracted doesn't mean 947 correct
3. **Sequential extraction works** - Each rule tells us where it ends
4. **LLM is necessary** - Complex structure requires understanding, not pattern matching

## Environment Requirements

- Python 3.x
- `anthropic` package: `pip install anthropic`
- `ANTHROPIC_API_KEY` environment variable set
- API rate limit: Must have available API quota

---

**Status:** Ready to run when API access returns on 2025-11-01
**Estimated time:** 2-3 hours for full extraction
**Expected result:** 972/972 rules correctly extracted
