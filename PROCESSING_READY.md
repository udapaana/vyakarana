# Ready to Process Rules Through Claude

## Current Status

✅ All 972 files extracted (966 actual rules + 6 placeholders)
✅ Markdown specification finalized with @[IAST] and @deva[Devanagari] notation
✅ Processing script created

## Next Steps

### 1. Set API Key
```bash
export ANTHROPIC_API_KEY='your-key-here'
```

### 2. Process Rules in Batches

Test with small batch first:
```bash
python3 scripts/process_rules_batch.py 1 10
```

Process in larger batches:
```bash
python3 scripts/process_rules_batch.py 1 100
python3 scripts/process_rules_batch.py 101 200
# ... continue through 972
```

Or process all at once (will take time):
```bash
for i in {1..972..50}; do
    end=$((i+49))
    if [ $end -gt 972 ]; then end=972; fi
    python3 scripts/process_rules_batch.py $i $end
    sleep 5
done
```

### 3. Output

Cleaned files will be in: `rules_cleaned/`

Progress tracked in: `cleanup_progress.json`

## What the Script Does

For each rule:
1. Fixes OCR errors (misread characters, spacing, etc.)
2. Converts romanized Sanskrit to proper IAST in @[...]
3. Wraps Devanagari in @deva[...]
4. Removes duplicate rule number headers (already in YAML)
5. Fixes markdown formatting
6. Preserves all content, examples, and references

## Specification Applied

- IAST: `@[saṃskṛta]`, `@[pāṇini]`, `@[guṇa]`
- Devanagari: `@deva[संस्कृत]`, `@deva[गुण]`
- YAML front matter preserved
- Rule numbers NOT duplicated in content
- Proper capitalization maintained

## Files

- Input: `rules/*.md` (972 files)
- Output: `rules_cleaned/*.md` (will be created)
- Spec: `MARKDOWN_SPEC.md`
- Script: `scripts/process_rules_batch.py`
