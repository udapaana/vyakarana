# Process Recovery & Restart Guide

## TL;DR - Quick Restart

If extraction is interrupted, you can safely restart:

```bash
# The extraction automatically resumes where it left off!
./parallel_extract.sh 4
```

The status tracking prevents re-extracting already completed rules.

---

## How Recovery Works

### Status Tracking System

The extraction maintains state in `data/phase3_extraction_status.json`:

```json
{
  "extracted_rules": ["rule_001", "rule_002", "rule_003", ...],
  "errors": {
    "8": {
      "error": "Validation failed - invalid content for § 8",
      "page_start": 14,
      "timestamp": "2025-11-01T06:07:34.142311",
      "retry_count": 1
    }
  },
  "total_extracted": 23,
  "total_errors": 1
}
```

**On restart, the extractor:**
1. Loads the status file
2. Checks if each rule is already extracted
3. **Skips completed rules**
4. **Continues from where it stopped**

---

## Restart Scenarios

### Scenario 1: Process Killed/Interrupted

**What happened:** You hit Ctrl-C or the process crashed mid-extraction.

**What to do:**
```bash
# Just restart - it will resume
./parallel_extract.sh 4
```

**What happens:**
- Loads status from `data/phase3_extraction_status.json`
- Sees rules 1-23 are already extracted
- Starts from rule 24 (first non-extracted rule)
- Continues to 972

**Safe:** ✅ Yes - already extracted rules won't be re-processed

---

### Scenario 2: Want to Start Completely Fresh

**What happened:** You want to delete everything and re-extract all 972 rules.

**What to do:**
```bash
# Clean everything
rm -rf phase3_rules/*.md
rm -f data/phase3_extraction_status.json
rm -f logs/*.log

# Start fresh
./parallel_extract.sh 4
```

**What happens:**
- No status file exists
- Starts from rule 1
- Extracts all 972 rules

**Safe:** ✅ Yes - but you lose all previous work

---

### Scenario 3: Fix Errored Rules Only

**What happened:** Some rules failed validation. You want to retry just those.

**What to do:**
```bash
# See which rules failed
python3 scripts/utilities/reprocess_rules.py --status

# Retry all errored rules
python3 scripts/utilities/reprocess_rules.py --retry-errors
```

**What happens:**
- Reads errors from status file
- Re-extracts only failed rules
- Updates status on success
- Keeps successful extractions

**Safe:** ✅ Yes - only re-processes errors

---

### Scenario 4: Fix Specific Rule

**What happened:** You notice rule 42 is incomplete or wrong.

**What to do:**
```bash
# Re-extract specific rule
python3 scripts/utilities/reprocess_rules.py --rule 42

# Or a range
python3 scripts/utilities/reprocess_rules.py --range 40-50
```

**What happens:**
- Re-extracts specified rule(s)
- Overwrites the existing file
- Updates status

**Safe:** ✅ Yes - surgical fix of specific rules

---

## Parallel Process Handling

### Multiple Processes Running

When you run `./parallel_extract.sh 4`, it starts 4 parallel processes:

```
Process 0: Rules starting from page 1
Process 1: Rules starting from page 136  
Process 2: Rules starting from page 271
Process 3: Rules starting from page 407
```

**Status File Safety:**
- Each process reads status at start
- Each process updates status after extracting each rule
- File locking ensures no corruption
- If one process crashes, others continue

**Killing Parallel Processes:**
```bash
# Kill all extraction processes
pkill -f parallel_extractor

# Or kill individual process by PID
kill <PID>
```

---

## Status File Corruption Prevention

### Problem: Multiple processes writing simultaneously

**Protection mechanisms:**
1. Each update is atomic (full file write)
2. Processes read-modify-write quickly
3. Status includes timestamp to detect conflicts

### If status file gets corrupted:

```bash
# Check if file is valid JSON
python3 -m json.tool data/phase3_extraction_status.json

# If corrupted, rebuild from extracted files
python3 scripts/utilities/rebuild_status.py
```

---

## Recovery Checklist

### Before Restarting:

- [ ] Check how many rules were extracted: `ls phase3_rules/rule_*.md | wc -l`
- [ ] Check status file exists: `cat data/phase3_extraction_status.json`
- [ ] Check for errors: `python3 scripts/utilities/reprocess_rules.py --status`
- [ ] Verify extraction processes aren't running: `ps aux | grep parallel`

### When Restarting:

**If you want to continue:**
```bash
./parallel_extract.sh 4  # Resumes automatically
```

**If you want to fix errors:**
```bash
python3 scripts/utilities/reprocess_rules.py --retry-errors
```

**If you want clean slate:**
```bash
rm -rf phase3_rules/*.md data/phase3_extraction_status.json logs/*.log
./parallel_extract.sh 4
```

---

## Monitoring During Extraction

### Real-time progress:

```bash
# Watch rule count
watch -n 5 'ls phase3_rules/rule_*.md | wc -l'

# Watch logs
tail -f logs/process_0_page_1.log

# Check status
python3 scripts/utilities/reprocess_rules.py --status
```

### Check if processes are running:

```bash
ps aux | grep parallel_extractor
# Or
pgrep -f parallel_extractor
```

---

## Common Issues

### Issue: "Rule already extracted, stopping"

**Cause:** Status file says rule is extracted, but file doesn't exist.

**Fix:**
```bash
# Option 1: Delete status, restart fresh
rm data/phase3_extraction_status.json
./parallel_extract.sh 4

# Option 2: Extract specific missing rule
python3 scripts/utilities/reprocess_rules.py --rule 42
```

### Issue: All rules fail with same error

**Cause:** Pipeline bug (like the parsing bug we just fixed).

**Fix:**
1. Kill processes: `pkill -f parallel_extractor`
2. Fix the code
3. Clean and restart: `rm -rf phase3_rules/* data/phase3_extraction_status.json`
4. Run: `./parallel_extract.sh 4`

### Issue: Extraction seems stuck

**Cause:** Claude CLI taking long time or waiting for auth.

**Check:**
```bash
# See what process is doing
tail -f logs/*.log

# Check Claude process
ps aux | grep claude
```

---

## File Safety

### What's Safe to Delete:

✅ `phase3_rules/rule_*.md` - Can regenerate
✅ `logs/*.log` - Just for debugging
✅ `phase3_rules/extraction_*.json` - Old format, deprecated
✅ `phase3_rules/debug_response_*.txt` - Debug files

### What to Keep:

⚠️ `data/phase3_extraction_status.json` - Tracks progress (but can rebuild)
⚠️ `phase2_structured/*.md` - Source data (hard to regenerate)
⚠️ `phase1_ocr/*` - Original OCR (hard to regenerate)

---

## Emergency Recovery

### Everything is broken, start over:

```bash
cd /Users/skmnktl/Downloads/ocr

# Kill all processes
pkill -f parallel_extractor

# Clean Phase 3 completely
rm -rf phase3_rules/*
rm -f data/phase3_extraction_status.json
rm -f logs/*.log

# Restart extraction with all fixes
./parallel_extract.sh 4
```

### Extract just one rule to test:

```bash
python3 scripts/utilities/reprocess_rules.py --rule 1
cat phase3_rules/rule_001.md
```

---

## Best Practices

1. **Don't manually edit status file** - Let the tools manage it
2. **Check logs before killing** - See if it's actually stuck or just slow
3. **Use status command often** - Know where you are: `reprocess_rules.py --status`
4. **Backup before major changes** - Copy status file before experiments
5. **Let parallel processes finish** - They coordinate through status file

---

## Summary

**The extraction is resumable!** 🎉

- Status tracking prevents duplicate work
- Can safely kill and restart
- Can fix specific rules without re-extracting everything
- Parallel processes coordinate safely
- Multiple recovery options available

**Most common workflow:**
1. Start: `./parallel_extract.sh 4`
2. If interrupted: `./parallel_extract.sh 4` (auto-resumes)
3. Fix errors: `python3 scripts/utilities/reprocess_rules.py --retry-errors`
4. Check progress: `python3 scripts/utilities/reprocess_rules.py --status`
