# Phase 3 Extraction - Status Tracking & Error Recovery

## Overview

Phase 3 extraction now includes comprehensive status tracking similar to Phase 2, allowing you to:
- Track which rules have been successfully extracted
- Monitor errors and retry them
- Reprocess individual rules or ranges
- Resume extraction from where it left off

## Status File

**Location:** `data/phase3_extraction_status.json`

### Structure

```json
{
  "extracted_rules": [
    "rule_001",
    "rule_002",
    ...
  ],
  "errors": {
    "7": {
      "error": "Validation failed - invalid content for § 7",
      "page_start": 13,
      "timestamp": "2025-11-01T12:00:00",
      "retry_count": 1
    }
  },
  "last_updated": "2025-11-01T12:30:00",
  "total_rules": 972,
  "total_extracted": 850,
  "total_errors": 12
}
```

### Fields

- **extracted_rules**: List of successfully extracted rule IDs
- **errors**: Map of rule number → error details
  - `error`: Error message
  - `page_start`: Page where extraction started
  - `timestamp`: When error occurred
  - `retry_count`: Number of retry attempts
- **last_updated**: Last modification timestamp
- **total_rules**: Total rules to extract (972)
- **total_extracted**: Count of successfully extracted rules
- **total_errors**: Count of rules with errors

## Commands

### Check Status

```bash
python3 scripts/utilities/reprocess_rules.py --status
```

Output:
```
======================================================================
PHASE 3 EXTRACTION STATUS
======================================================================

Total rules: 972
Extracted: 850 (87.4%)
Errors: 12
Remaining: 110
Last updated: 2025-11-01T12:30:00

======================================================================
ERRORED RULES
======================================================================

§ 7
  Error: Validation failed - invalid content for § 7
  Page: 13
  Retries: 1
  Time: 2025-11-01T12:00:00

§ 142
  Error: Schema validation failed: Missing: source_pages
  Page: 98
  Retries: 0
  Time: 2025-11-01T12:15:00
...
```

### Retry All Errors

```bash
python3 scripts/utilities/reprocess_rules.py --retry-errors
```

This will:
1. Load all errored rules from status
2. Attempt to extract each one
3. Update status (mark as extracted or increment retry count)
4. Show summary of successes/failures

### Reprocess Single Rule

```bash
python3 scripts/utilities/reprocess_rules.py --rule 7
```

Useful when:
- Fixing a specific rule manually
- Testing extraction after fixing upstream data
- Debugging individual rule issues

### Reprocess Range

```bash
python3 scripts/utilities/reprocess_rules.py --range 1-10
```

Useful for:
- Reprocessing a chapter or section
- Batch reprocessing after fixing issues
- Testing extraction on subset

## Integration with Extraction

The parallel extractor automatically:

### On Success
1. Validates schema (YAML structure)
2. Validates content (no errors, proper format)
3. Saves rule file to `phase3_rules/rule_NNN.md`
4. Marks rule as extracted in status
5. Updates `total_extracted` count

### On Failure
1. Catches validation or extraction error
2. Marks rule as errored in status
3. Increments retry count if retrying
4. Updates `total_errors` count
5. Continues to next rule (doesn't crash)

### Smart Skipping
- Checks status before extracting each rule
- Skips already-extracted rules
- Allows parallel processes to work without conflicts
- Enables resume after interruption

## Workflow Examples

### Initial Extraction
```bash
# Start extraction
./parallel_extract.sh

# Some rules fail due to OCR issues
# Status shows: 950 extracted, 22 errors

# Check what failed
python3 scripts/utilities/reprocess_rules.py --status
```

### Fix and Retry
```bash
# Fix upstream OCR or structured pages
# Then retry errors
python3 scripts/utilities/reprocess_rules.py --retry-errors

# Result: 18 succeed, 4 still fail
# Status now: 968 extracted, 4 errors
```

### Manual Fix
```bash
# Manually investigate remaining errors
python3 scripts/utilities/reprocess_rules.py --status

# Fix specific rule
python3 scripts/utilities/reprocess_rules.py --rule 7

# Verify
python3 scripts/utilities/reprocess_rules.py --status
```

### Reprocess Section
```bash
# Decided to improve extraction prompt
# Reprocess entire "Alphabet" chapter (rules 1-20)
python3 scripts/utilities/reprocess_rules.py --range 1-20

# Or just retry what failed
python3 scripts/utilities/reprocess_rules.py --retry-errors
```

## Benefits

### Robustness
- ✅ Extraction doesn't fail completely on errors
- ✅ Progress is saved continuously
- ✅ Can resume from any point
- ✅ Safe parallel execution

### Observability
- ✅ Clear status at any time
- ✅ Detailed error information
- ✅ Retry count tracking
- ✅ Timestamp for debugging

### Efficiency
- ✅ Skip already-extracted rules
- ✅ Only retry what failed
- ✅ Batch operations supported
- ✅ No duplicate work

### Maintainability
- ✅ Structured error tracking
- ✅ Easy to debug specific rules
- ✅ Clean separation of concerns
- ✅ Similar to Phase 2 (consistent pattern)

## Status vs Legacy Logs

The extractor maintains both:

1. **Status File** (New): `data/phase3_extraction_status.json`
   - Canonical source of truth
   - Used for reprocessing
   - Structured and queryable

2. **Legacy Logs** (Old): `phase3_rules/extraction_*.json`
   - Progress log: Detailed per-rule progress
   - Error log: Timestamped errors
   - Kept for compatibility

**Recommendation**: Use status file for all new workflows.

## Advanced Usage

### Custom Status File
```bash
python3 scripts/utilities/reprocess_rules.py \
  --status-file custom_status.json \
  --retry-errors
```

### Custom Output Directory
```bash
python3 scripts/utilities/reprocess_rules.py \
  --output-dir custom_rules/ \
  --rule 7
```

### Programmatic Access
```python
from pathlib import Path
from scripts.ai.parallel_extractor import ParallelExtractor

# Load extractor with status
extractor = ParallelExtractor(
    structured_pages_dir=Path("phase2_structured"),
    output_dir=Path("phase3_rules"),
    status_file=Path("data/phase3_extraction_status.json")
)

# Check status
if extractor.is_rule_extracted(7):
    print("Rule 7 already extracted")

# Get errors
errored = extractor.get_errored_rules()
print(f"Errored rules: {errored}")

# Access raw status
print(extractor.status)
```

## Monitoring

### Check Progress During Extraction
```bash
# In one terminal
./parallel_extract.sh

# In another terminal
watch -n 5 'python3 scripts/utilities/reprocess_rules.py --status | head -20'
```

### Count Extracted Rules
```bash
ls phase3_rules/rule_*.md | wc -l
```

### Find Missing Rules
```bash
python3 << 'EOF'
import json
from pathlib import Path

status = json.load(open('data/phase3_extraction_status.json'))
extracted = set(int(r.split('_')[1]) for r in status['extracted_rules'])
all_rules = set(range(1, 973))
missing = sorted(all_rules - extracted)

print(f"Missing {len(missing)} rules:")
print(missing[:20])  # First 20
if len(missing) > 20:
    print(f"... and {len(missing) - 20} more")
EOF
```

## Troubleshooting

### Status file corrupted
```bash
# Backup old status
mv data/phase3_extraction_status.json data/phase3_extraction_status.json.bak

# Extractor will create new one
# Then merge manually if needed
```

### Extractor says rule extracted but file missing
```python
# Remove from status to allow reprocessing
import json
status = json.load(open('data/phase3_extraction_status.json'))
status['extracted_rules'].remove('rule_007')
json.dump(status, open('data/phase3_extraction_status.json', 'w'), indent=2)
```

### Want to re-extract everything
```bash
# Clear status and rules
rm data/phase3_extraction_status.json
rm phase3_rules/rule_*.md

# Start fresh
./parallel_extract.sh
```
