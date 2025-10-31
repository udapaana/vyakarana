# Phase 2 Processing Scripts

Scripts for reconciling dual OCR sources and structuring into markdown.

## Scripts

### `process_batch.py` - Main Processing Script

Reconciles Google + Claude OCR and structures pages into markdown with YAML metadata.

**Usage:**

```bash
# Process next batch of 10 pages
python3 process_batch.py --batch-size 10

# Process from specific page
python3 process_batch.py --start-page 100 --batch-size 50

# Process specific pages
python3 process_batch.py --pages "101,159,160,397,448"

# Reprocess pages that had errors
python3 process_batch.py --reprocess-errors

# Check status only
python3 process_batch.py --status
```

**Features:**
- Uses Claude CLI (Max subscription, not API)
- Automatic status tracking in `data/processing_status.json`
- Validation reports saved per page
- Removes pages from error list on successful retry
- Skips already-processed pages

### `fix_processing_status.py` - Status Reconciliation

Synchronizes `processing_status.json` with actual files in `structured_pages/`.

**Usage:**

```bash
python3 fix_processing_status.py
```

**What it does:**
- Scans `structured_pages/` for actual .md files
- Updates `processed_pages` list to match reality
- Removes duplicate error entries
- Removes errors for successfully processed pages
- Shows summary and error breakdown

**When to run:**
- After manual file operations
- When status file seems out of sync
- After recovering from interruptions

## Rerunnability

Phase 2 is **fully rerunnable**:

### Full Rerun
```bash
# Delete output and status
rm -rf structured_pages/
rm data/processing_status.json

# Start fresh
python3 process_batch.py --start-page 1 --batch-size 50
```

### Partial Rerun
```bash
# Delete specific pages
rm structured_pages/page_{101,397,448}.md

# Reprocess just those pages
python3 process_batch.py --pages "101,397,448"
```

### Retry Errors
```bash
# Check what failed
python3 process_batch.py --status

# Retry all errors
python3 process_batch.py --reprocess-errors
```

The script automatically:
- Skips already-processed pages (unless in error list)
- Updates status file after each page
- Removes from error list on success
- Preserves progress across runs

## Prerequisites

```bash
# Install dependencies
pip install anthropic python-dotenv

# Set up Claude CLI (for Max subscription)
# Do NOT set ANTHROPIC_API_KEY - let it use Max subscription
```

## Input

Requires Phase 1 OCR output:
- `ocr_output/claude/page_NNN.txt`
- `ocr_output/google/page_NNN.txt`

Both files must exist for each page to be processed.

## Output

For each page creates:
- `structured_pages/page_NNN.md` - Structured markdown with YAML front matter
- `structured_pages/page_NNN_validation.json` - Validation report

Also maintains:
- `data/processing_status.json` - Overall progress tracking
- `data/consistency_data.json` - Index of terms, citations

## Troubleshooting

### "OCR files missing for page N"
- Check that both `ocr_output/claude/page_NNN.txt` and `ocr_output/google/page_NNN.txt` exist
- If one is missing, rerun Phase 1 for that page

### "CLI error code 1"
- May need to accept Claude Terms of Service update
- Run `claude` interactively to accept terms
- Then retry with `--reprocess-errors`

### Status file out of sync
```bash
# Fix it
python3 fix_processing_status.py
```

### Want to reprocess already-done pages
```bash
# Delete specific pages and reprocess
rm structured_pages/page_050.md
python3 process_batch.py --pages "50"
```

## Performance

- **Time per page**: ~60-90 seconds (Claude CLI call)
- **Parallelization**: Can run 3-5 instances with Claude Max 5x
- **Rate limits**: Claude Max subscription has generous limits
- **Cost**: Uses Claude Max subscription (no API charges)

## Next Steps

After Phase 2 completion, use output for:
- Phase 3: Extract individual rules (§1-§972)
- Build comprehensive index from YAML metadata
- Generate table of contents
- Create searchable database
