# Parallel Rule Extraction

## Overview

Run multiple extraction processes in parallel from different starting pages. Each process automatically:
- Finds the first rule at/after its starting page
- Extracts rules sequentially
- Skips already-extracted rules
- Stops when hitting a completed rule
- Logs errors with start pages for retry

## Quick Start

### Run 4 Parallel Processes

```bash
cd /Users/skmnktl/Downloads/ocr

# Terminal 1: Start from page 1
python3 -m scripts.ai.parallel_extractor 1 &

# Terminal 2: Start from page 200
python3 -m scripts.ai.parallel_extractor 200 &

# Terminal 3: Start from page 400
python3 -m scripts.ai.parallel_extractor 400 &

# Terminal 4: Start from page 600
python3 -m scripts.ai.parallel_extractor 600 &
```

Each process will:
1. Find the first rule on/after its starting page
2. Extract rules until it hits one that's already been extracted by another process
3. Stop automatically (no conflicts!)

## How It Works

### Starting from Page 200

```
1. Read page 200
2. Find first rule mentioned: "§ 143"
3. Extract § 143, § 144, § 145...
4. Continue until hitting already-extracted rule
5. Stop
```

### Parallel Safety

Process A (page 1):    Rules 1 → 142
Process B (page 200):  Rules 143 → 287
Process C (page 400):  Rules 288 → 431
Process D (page 600):  Rules 432 → 972

When Process B reaches Rule 288, it sees it's already been extracted by Process C → **stops automatically**

## Usage

### Basic Syntax

```bash
python3 -m scripts.ai.parallel_extractor <start_page> [output_dir]
```

### Examples

```bash
# Start from page 1
python3 -m scripts.ai.parallel_extractor 1

# Start from page 300, output to custom dir
python3 -m scripts.ai.parallel_extractor 300 rules_custom

# Run multiple in parallel
python3 -m scripts.ai.parallel_extractor 1 &
python3 -m scripts.ai.parallel_extractor 250 &
python3 -m scripts.ai.parallel_extractor 500 &
```

## Output Files

```
rules/
├── rule_001.md              # Extracted rules
├── rule_002.md
├── ...
├── extraction_progress.json # Successful extractions with start/end pages
└── extraction_errors.json   # Failed extractions with start pages
```

### Progress Log Format

`extraction_progress.json`:
```json
{
  "1": {
    "start_page": 1,
    "end_page": 8,
    "timestamp": "2024-10-31T18:30:00"
  },
  "77": {
    "start_page": 49,
    "end_page": 51,
    "timestamp": "2024-10-31T18:45:00"
  }
}
```

### Error Log Format

`extraction_errors.json`:
```json
[
  {
    "rule": 326,
    "start_page": 150,
    "error": "Claude CLI timeout",
    "timestamp": "2024-10-31T19:00:00"
  }
]
```

## Monitoring Progress

### Check Total Extracted

```bash
ls rules/rule_*.md | wc -l
```

### View Progress Log

```bash
# Pretty print
cat rules/extraction_progress.json | python3 -m json.tool | head -20

# Count successful extractions
cat rules/extraction_progress.json | grep "start_page" | wc -l
```

### View Errors

```bash
# Show all errors
cat rules/extraction_errors.json | python3 -m json.tool

# Count errors
cat rules/extraction_errors.json | grep "rule" | wc -l
```

### Real-time Monitoring

```bash
# Watch extraction count
watch -n 5 "ls rules/rule_*.md | wc -l"

# Follow one process
tail -f extraction_200.log  # If you redirect output
```

## Retry Failed Rules

After extraction completes, retry any failed rules:

```bash
# View errors
cat rules/extraction_errors.json

# Retry from the start page of a failed rule
python3 -m scripts.ai.parallel_extractor 150  # If rule 326 failed at page 150
```

## Performance

### Speed Comparison

| Method | Time | Processes |
|--------|------|-----------|
| Sequential | 16-24 hours | 1 |
| 2 Parallel | 8-12 hours | 2 |
| 4 Parallel | 4-6 hours | 4 |
| 8 Parallel | 2-3 hours | 8 |

### Recommended Setup

**For fastest completion**: 4-8 parallel processes

```bash
# Divide 729 pages by number of processes
# 729 / 4 = ~182 pages per process

python3 -m scripts.ai.parallel_extractor 1 > p1.log 2>&1 &
python3 -m scripts.ai.parallel_extractor 182 > p2.log 2>&1 &
python3 -m scripts.ai.parallel_extractor 364 > p3.log 2>&1 &
python3 -m scripts.ai.parallel_extractor 546 > p4.log 2>&1 &

# Monitor
tail -f p*.log
```

## Example Session

```bash
$ python3 -m scripts.ai.parallel_extractor 200

🔍 Finding first rule on/after page 200...
✓ Found Rule § 143 starting at page 200

🚀 Starting extraction from Rule § 143
📄 Current page: 200
♻️  Fresh context per rule

[143] Extracting Rule § 143 (from page 200)... ✓ (ends at page 202)
[144] Extracting Rule § 144 (from page 202)... ✓ (ends at page 203)
[145] Extracting Rule § 145 (from page 203)... ✓ (ends at page 204)
...
[287] Extracting Rule § 287 (from page 350)... ✓ (ends at page 351)
[288] Rule § 288 already exists, stopping.

✅ Extraction complete from this starting point!
📊 Extracted: 145 rules
⏭️  Skipped: 1 rules (already existed)
```

## Advantages

✅ **4-8x faster** with parallel processes
✅ **No conflicts** - auto-stops at completed rules
✅ **Error recovery** - logs failed rules with start pages
✅ **Flexible** - start from any page
✅ **Progress tracking** - see what each process extracted

## Tips

### Start Conservative

Test with 2 processes first:
```bash
python3 -m scripts.ai.parallel_extractor 1 &
python3 -m scripts.ai.parallel_extractor 400 &
```

### Use Screen/Tmux

```bash
# Create session for each process
screen -S p1
python3 -m scripts.ai.parallel_extractor 1
# Ctrl+A, D to detach

screen -S p2
python3 -m scripts.ai.parallel_extractor 200
# Ctrl+A, D

# Reattach
screen -r p1
```

### Check Completion

```bash
# Should be 972
ls rules/rule_*.md | wc -l

# Should be empty (or show only retryable errors)
cat rules/extraction_errors.json
```

## Troubleshooting

### Process seems stuck

Check if Claude CLI is responding:
```bash
ps aux | grep claude
```

### Hit rate limit

Unlikely with browser auth, but if it happens, reduce parallel processes.

### Rules being skipped incorrectly

Check file sizes:
```bash
# Find small/empty files
find rules -name "rule_*.md" -size -100c
```

## Complete Example

```bash
#!/bin/bash
# parallel_extract.sh - Run 4 parallel extraction processes

cd /Users/skmnktl/Downloads/ocr

# Start 4 processes
python3 -m scripts.ai.parallel_extractor 1 > logs/p1.log 2>&1 &
P1=$!

python3 -m scripts.ai.parallel_extractor 200 > logs/p2.log 2>&1 &
P2=$!

python3 -m scripts.ai.parallel_extractor 400 > logs/p3.log 2>&1 &
P3=$!

python3 -m scripts.ai.parallel_extractor 600 > logs/p4.log 2>&1 &
P4=$!

echo "Started 4 parallel processes:"
echo "  Process 1 (PID $P1): page 1"
echo "  Process 2 (PID $P2): page 200"
echo "  Process 3 (PID $P3): page 400"
echo "  Process 4 (PID $P4): page 600"
echo ""
echo "Monitor progress: tail -f logs/p*.log"
echo "Check completion: ls rules/rule_*.md | wc -l"

# Wait for all to complete
wait $P1 $P2 $P3 $P4

echo "All processes complete!"
ls rules/rule_*.md | wc -l
```

---

**Status**: ✅ Ready for parallel extraction
**Speed**: 4-8x faster than sequential
**Cost**: $0 (browser auth)
**Time**: 2-6 hours with 4-8 processes
