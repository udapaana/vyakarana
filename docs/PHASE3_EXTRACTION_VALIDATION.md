# Phase 3 Extraction - Validation & Quality Control

## Overview

Phase 3 extraction now includes comprehensive validation to ensure only valid rule content is saved. This prevents writing error messages, partial content, or mismatched rules.

## Validation Rules

Before saving any extracted rule, the system validates:

### 1. No Error Messages
Rejects content containing error phrases:
- "NOT present"
- "not found"
- "not included"
- "missing from"
- "not appear"
- "Rule § N is not"

**Example of rejected content:**
```
I need to search for rule § 7 in the provided pages.

**Rule § 7 is not present in any of the provided pages.**
```

### 2. Rule Number Match
Verifies the requested rule number appears in the content via:
- YAML frontmatter: `rule: "§ 7"`
- Section heading: `## § 7. Title`
- Direct reference: `§ 7`

**Example of valid content:**
```yaml
---
rule: "§ 7"
title: "Aspiration of Consonants"
---

## § 7. Aspiration of Consonants

Some consonants are pronounced...
```

### 3. Minimum Content Length
Ensures substantial content (minimum 100 characters after stripping whitespace).

**Rejected:** Short stubs or incomplete extractions

### 4. Proper Format
Requires YAML frontmatter (must start with `---`).

**Rejected:** Raw text without structure

## Validation Flow

```
Extract Rule Content
        ↓
Parse JSON metadata (end_page)
        ↓
Strip markdown code fences
        ↓
VALIDATE CONTENT ← NEW STEP
        ↓
   Valid?
   ↙    ↘
 YES    NO
  ↓      ↓
Save   Skip & Log Error
File
```

## Error Handling

When validation fails:
1. **File is NOT written** (prevents bad data)
2. Error is logged to `phase3_rules/extraction_errors.json`
3. Includes: rule number, start page, error message, timestamp
4. Extraction continues with next rule

Example error log entry:
```json
{
  "rule": 7,
  "start_page": 13,
  "error": "Validation failed - invalid content for § 7",
  "timestamp": "2025-11-01T12:00:00"
}
```

## Testing

Validation logic is tested against 5 scenarios:

1. ✅ Error message detection
2. ✅ Valid content acceptance
3. ✅ Content length enforcement
4. ✅ YAML frontmatter requirement
5. ✅ Rule number matching

All tests pass as verified in the implementation.

## Benefits

### Before Validation
- ❌ Error messages saved as rules (e.g., rule_007.md)
- ❌ Partial/incomplete extractions saved
- ❌ Wrong rules saved to wrong files
- ❌ Manual cleanup required

### After Validation
- ✅ Only valid rules saved
- ✅ Consistent quality
- ✅ Clear error logging
- ✅ No manual cleanup needed
- ✅ Safe to run extraction in parallel

## Usage

Validation is automatic - no configuration needed:

```bash
# Run extraction - validation happens automatically
./parallel_extract.sh

# Check errors if any rules failed
cat phase3_rules/extraction_errors.json
```

## Implementation Details

**Location:** `scripts/ai/parallel_extractor.py`

**Key Method:** `validate_extracted_content(rule_num, content)`

**Integration Point:** Before `rule_file.write()` in `extract_from_page()`

```python
# Extract rule
content, end_page = self.extract_rule(current_rule, current_page)

# VALIDATION: Only save if content is valid
if not self.validate_extracted_content(current_rule, content):
    raise RuntimeError(f"Validation failed - invalid content for § {current_rule}")

# Save rule (only reached if valid)
rule_file = self.output_dir / f"rule_{current_rule:03d}.md"
with open(rule_file, "w", encoding="utf-8") as f:
    f.write(content)
```

## Future Enhancements

Potential additional validations:
- Check for required YAML fields (title, chapter, etc.)
- Validate Devanagari/IAST markup format
- Verify examples are present for rule types that require them
- Cross-reference with phase2_structured to ensure completeness
