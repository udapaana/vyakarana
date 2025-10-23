# Rule Cleanup Status

## Current Progress

**23.5% complete** (228/972 files cleaned)

- ✅ Completed: 123 rules
- ⊘ Skipped: 1 placeholder  
- ✗ Failed: 1 rule (§212 - will retry)
- 🔄 In Progress: Background job processing

## Background Job Running

Currently processing missing rules with:
- 2.5 second delay between API calls
- Processing in batches of 50
- Auto-retry on completion

## How to Monitor

Check progress anytime:
```bash
python3 scripts/check_progress.py
```

Check background job status:
```bash
# The job is running and processing rules automatically
# It will continue until all missing rules are processed
```

## To Process All Remaining

The automated script will process all remaining rules:
```bash
./scripts/process_all_missing.sh
```

This processes in batches of 100 with proper rate limiting.

## Estimated Time

- ~2.5 seconds per rule
- ~744 rules remaining
- Estimated: ~30-40 minutes total

## What's Being Done

For each rule:
1. Fix OCR errors
2. Convert Sanskrit to IAST in @[...]
3. Wrap Devanagari in @deva[...]
4. Remove duplicate rule headers
5. Fix markdown formatting
6. Save to `rules_cleaned/`

## Repository

Already pushed to: https://github.com/udapaana/vyakarana

Push cleaned files when done:
```bash
git add rules_cleaned/
git add cleanup_progress.json
git commit -m "Add Claude-cleaned rules (in progress)"
git push
```
