# Quick Start - Resume Rule Extraction

## When API Access Returns (2025-11-01)

### 1. Verify Environment
```bash
cd /Users/skmnktl/Downloads/ocr
echo $ANTHROPIC_API_KEY  # Should show your key
python3 -c "import anthropic; print('✓ anthropic package installed')"
```

### 2. Run Extraction
```bash
# Full extraction (all 972 rules)
python scripts/extraction/extract_rules_llm.py --start 1 --end 972 --output rules_llm
```

### 3. Monitor Progress
- Progress shown every 10 rules
- Estimated time: 2-3 hours
- Output: `rules_llm/rule_1.md` through `rules_llm/rule_972.md`

### 4. Verify Results
```bash
# Count extracted rules (should be 972)
ls rules_llm/rule_*.md | wc -l

# Check for empty files (should be none)
find rules_llm -name "rule_*.md" -size 0

# Spot check a few rules
head -20 rules_llm/rule_5.md
head -20 rules_llm/rule_326.md
```

## If Interrupted

If extraction is interrupted at rule N, resume from that point:
```bash
python scripts/extraction/extract_rules_llm.py --start N --end 972 --output rules_llm
```

## Current State

- ✅ Phase 1: PDF to images (complete)
- ✅ Phase 2: Images to structured pages (complete - 729 pages)
- 🔄 Phase 3: Pages to individual rules (ready to run)

**Files ready:**
- `scripts/extraction/extract_rules_llm.py` - Main extraction script
- `EXTRACTION_PLAN.md` - Full documentation
- `rules_llm/rule_1.md` - Example of correct extraction

**What's wrong with current rules/ directory:**
- 947/972 rules extracted (25 missing)
- Unknown correctness (e.g., rule 6 had wrong content)
- Need full LLM-based re-extraction

## After Successful Extraction

```bash
# Archive old extraction
mv rules rules_old_regex_based

# Use new extraction
mv rules_llm rules

# Verify
ls rules/rule_*.md | wc -l  # Should show 972
```

---

**Next command to run:** `python scripts/extraction/extract_rules_llm.py --start 1 --end 972 --output rules_llm`
