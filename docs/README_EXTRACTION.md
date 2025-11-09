# Phase 3 Rule Extraction - Ready to Run

## 🚀 Quick Start (Recommended)

### Parallel Extraction (4-6 hours)

```bash
cd /Users/skmnktl/Downloads/ocr

# Run 4 parallel processes (fastest)
./parallel_extract.sh 4

# Or 8 processes (even faster if your system can handle it)
./parallel_extract.sh 8
```

### Sequential Extraction (10-24 hours)

```bash
# Single process
python3 extract_rules.py
```

## What You Have

Two extraction methods, both using **browser-authenticated Claude CLI** (zero cost):

### 1. Parallel Extractor ⚡ (Recommended)

**Speed**: 4-8x faster with multiple processes

```bash
# Launch 4 parallel processes
./parallel_extract.sh 4
```

Features:
- ✅ Start from any page
- ✅ Auto-finds first rule
- ✅ Skips completed rules
- ✅ Stops at conflicts
- ✅ Logs errors with start pages
- ✅ 2-6 hours completion time

### 2. Sequential Extractor 🐢

**Speed**: Single-threaded, page-by-page

```bash
python3 extract_rules.py
```

Features:
- ✅ Simple and reliable
- ✅ Fresh context per rule
- ✅ Auto-resume on interruption
- ✅ 10-24 hours completion time

## Files

```
├── parallel_extract.sh              # Launch parallel processes
├── extract_rules.py                 # Sequential extraction
├── scripts/ai/
│   ├── parallel_extractor.py       # Parallel-safe logic
│   └── batch_sequential.py         # Sequential logic
├── PARALLEL_EXTRACTION.md           # Parallel docs
└── SIMPLE_EXTRACTION.md             # Sequential docs
```

## Output

```
rules/
├── rule_001.md ... rule_972.md     # Extracted rules
├── extraction_progress.json         # Success log with page ranges
└── extraction_errors.json           # Error log with start pages
```

## Monitoring

```bash
# Count extracted rules
ls rules/rule_*.md | wc -l

# Watch in real-time
watch -n 5 "ls rules/rule_*.md | wc -l"

# View progress
cat rules/extraction_progress.json | python3 -m json.tool | head

# Check errors
cat rules/extraction_errors.json
```

## Cost & Time

| Method | Processes | Time | Cost |
|--------|-----------|------|------|
| Parallel | 8 | 2-3 hrs | $0 |
| Parallel | 4 | 4-6 hrs | $0 |
| Parallel | 2 | 8-12 hrs | $0 |
| Sequential | 1 | 10-24 hrs | $0 |

All methods use browser-authenticated Claude CLI (subscription-based).

## Which to Use?

**Want speed?** → `./parallel_extract.sh 4`
**Want simplicity?** → `python3 extract_rules.py`
**Want maximum speed?** → `./parallel_extract.sh 8`

## Examples

### Run 4 Parallel Processes

```bash
./parallel_extract.sh 4
```

Output:
```
============================================================
PARALLEL RULE EXTRACTION
============================================================
Processes: 4
Pages per process: ~182
Output: rules/
============================================================

Starting Process 1: page 1 → logs/process_0_page_1.log
Starting Process 2: page 183 → logs/process_1_page_183.log
Starting Process 3: page 365 → logs/process_2_page_365.log
Starting Process 4: page 547 → logs/process_3_page_547.log

All processes started!

Monitor progress:
  tail -f logs/*.log
  watch -n 5 'ls rules/rule_*.md | wc -l'
```

### Manual Parallel Launch

```bash
# Terminal 1
python3 -m scripts.ai.parallel_extractor 1 &

# Terminal 2
python3 -m scripts.ai.parallel_extractor 200 &

# Terminal 3
python3 -m scripts.ai.parallel_extractor 400 &

# Terminal 4
python3 -m scripts.ai.parallel_extractor 600 &
```

## After Completion

### Verify

```bash
# Should show 972
ls rules/rule_*.md | wc -l

# Check for errors
cat rules/extraction_errors.json

# View sample
cat rules/rule_001.md
cat rules/rule_077.md
```

### Retry Failed Rules

If any rules failed:

```bash
# Check error log for start pages
cat rules/extraction_errors.json

# Retry from that page
python3 -m scripts.ai.parallel_extractor 150
```

## Architecture

### Parallel Extractor Flow

```
Process A (page 1):
  → Find first rule (§1)
  → Extract §1, §2, §3...
  → Check if §142 exists
  → Not found, extract it
  → Check if §143 exists
  → Found! Stop.

Process B (page 200):
  → Find first rule (§143)
  → Extract §143, §144...
  → Continue until done or conflict
```

### Sequential Extractor Flow

```
Rule 1: page 1 → extract → ends page 8
Rule 2: page 8 → extract → ends page 9
Rule 3: page 9 → extract → ends page 11
...continue...
```

## Troubleshooting

### Processes finish too quickly

One process might be hitting already-completed rules from another. This is normal and means overlap is working!

### No rules extracted

Check logs:
```bash
tail -100 logs/*.log
```

### Claude CLI errors

Make sure `ANTHROPIC_API_KEY` is unset:
```bash
unset ANTHROPIC_API_KEY
./parallel_extract.sh 4
```

## Documentation

- **[PARALLEL_EXTRACTION.md](PARALLEL_EXTRACTION.md)** - Detailed parallel guide
- **[SIMPLE_EXTRACTION.md](SIMPLE_EXTRACTION.md)** - Sequential guide
- **[EXTRACTION_WITH_BROWSER_AUTH.md](EXTRACTION_WITH_BROWSER_AUTH.md)** - Browser auth setup

## Summary

✅ **Two methods ready**: Parallel (fast) or Sequential (simple)
✅ **Zero cost**: Browser-authenticated Claude CLI
✅ **Auto-resume**: Never lose progress
✅ **Error logging**: Retry failed rules easily
✅ **Tested**: Rule extraction working

**Recommended command**: `./parallel_extract.sh 4`

---

**Status**: Production ready
**Time to complete**: 2-24 hours (depending on method)
**Cost**: $0
**Created**: 2024-10-31
