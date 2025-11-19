# Phase 2 YAML Validation Guide

## Common YAML Errors and How to Fix Them

### Error Types

#### 1. **page_number doesn't match filename**

**Example:**
```
❌ page_024.md: page_number=25 doesn't match filename (expected 24)
```

**Cause:** YAML frontmatter was copied incorrectly

**Fix:**
```bash
# Edit the file
vim phase2_cleaned/page_024.md

# Change:
page_number: 25
# To:
page_number: 24
```

#### 2. **rules_starting doesn't match actual content**

**Example:**
```
❌ page_023.md: rules_starting=[] but actual content has ['§ 21']
```

**Cause:** Rule actually STARTS on this page (has `§ 21.` pattern) but YAML says it's empty

**Fix:**
```yaml
# Before:
rules_starting: []
rules_continuing: ["§ 21"]

# After:
rules_starting: ["§ 21"]
rules_continuing: []
```

**How to identify:** Look for `§ N.` or `§ N ` (with period or space) at the start of lines in the content

#### 3. **Duplicate content across files**

**Example:**
```
❌ DUPLICATE CONTENT: page_024.md, page_025.md have identical content
```

**Cause:** Same source file was accidentally written to multiple output files

**Fix:**
```bash
# 1. Check mapping for correct sources
python3 -c "
import json
with open('phase2_corrected_mapping.json') as f:
    mapping = json.load(f)
for entry in mapping[23:26]:
    print(f\"Page {entry['output_page']}: {entry['source_path']} -> {entry['output_file']}\")
"

# 2. Delete the duplicate
rm phase2_cleaned/page_024.md

# 3. Re-clean from correct source
# Read phase1_ocr/claude/page_022.txt
# Write to phase2_cleaned/page_024.md
```

## Validation Workflow

### After Cleaning Each Batch

```bash
# Run YAML validation
python3 scripts/validate_page_yaml.py
```

**What it checks:**
1. ✓ page_number matches filename
2. ✓ rules_starting matches actual `§ N.` or `§ N ` patterns in content
3. ✓ No duplicate content across files

### Expected Output

**Success:**
```
================================================================================
PHASE 2 PAGE YAML VALIDATION
================================================================================

Validating 30 pages...


================================================================================
VALIDATION SUMMARY
================================================================================

✅ ALL VALIDATIONS PASSED
   30 pages validated successfully
```

**Failure:**
```
================================================================================
VALIDATION SUMMARY
================================================================================

❌ ERRORS FOUND:

  ❌ page_023.md: rules_starting=[] but actual content has ['§ 21']
  ❌ page_024.md: page_number=25 doesn't match filename (expected 24)
  ❌ DUPLICATE CONTENT: page_024.md, page_025.md have identical content

❌ VALIDATION FAILED: 3 errors, 0 warnings
```

## How to Fix Each Error Type

### Quick Fix Checklist

**For page_number mismatch:**
1. Open the file: `vim phase2_cleaned/page_NNN.md`
2. Fix `page_number:` in YAML to match filename
3. Save and re-validate

**For rules_starting mismatch:**
1. Open the file: `vim phase2_cleaned/page_NNN.md`
2. Search for `^§` patterns in content (after second `---`)
3. Update `rules_starting: [...]` to match actual patterns
4. If rule STARTS here: add to `rules_starting`
5. If rule CONTINUES here: add to `rules_continuing`
6. Save and re-validate

**For duplicate content:**
1. Check mapping: `python3 -c "..."`  (see above)
2. Delete incorrect file: `rm phase2_cleaned/page_NNN.md`
3. Re-clean from correct source
4. Re-validate

## OCR Quality Issues

### Issue: Missing Rule Markers in Claude OCR

**Symptom:** A rule number appears to be skipped (e.g., § 69 → § 71 with no § 70)

**Example:**
- page_047.md appears to skip from § 69 to § 71
- But internal page 39 should contain § 70

**Cause:** Claude OCR sometimes fails to detect `§ N.` markers when:
- Text is faint or low contrast
- The period after the number is missing/unclear
- OCR confidence is low for that region

**Fix Strategy:**

1. **Check the official_1931 source** (higher quality OCR):
```bash
# Find the internal page number from mapping
cat phase2_cleaned/page_047.md | grep "internal_page:"
# Output: internal_page: 39

# Check official_1931 OCR for that internal page
cat phase1_ocr/sources/official_1931/039.txt | grep "§ 70"
```

2. **If found in official_1931**, update the cleaned page:
```yaml
# Before:
rules_starting: []
rules_continuing: ["§ 69"]

# After:
rules_starting: ["§ 70"]
rules_continuing: ["§ 69"]
```

3. **Add the complete rule text** from official_1931 source

**Example Fix (page_047.md):**
```diff
- Adjectives ending in इ and उ when used with
- re optionally declined like mas. nouns in इ and
+ § 70. Adjectives ending in इ and उ when used with neuter nouns
+ are optionally declined like mas. nouns in इ and उ in the Da. Ab.
+ Gen. and Loc. singulars and Gen. Loc. duals, e.g. शुचि neu.
+ white, pure; गुरु neu. heavy:—
```

**Prevention:** When a rule number appears to be missing:
1. ✓ Check official_1931 source first
2. ✓ Cross-reference with phase2_corrected_mapping.json
3. ✓ Verify internal_page matches expected rule sequence

## Pattern Recognition

### Rule Starting Patterns

A rule STARTS on a page if you see:

```
§ 21. When अ or आ is followed...
```
OR
```
§ 27 The particle उ, preceded...
```

**Pattern:** `§ N.` or `§ N ` at the **start of a line** (not in footnotes)

### Rule Continuing

A rule CONTINUES if:
- Previous page had § N starting
- This page has NO `§ N.` or `§ N ` pattern
- Content flows from previous page

## Integration with Main Validation

The Page YAML validator (`validate_page_yaml.py`) is **separate from** the Phase 2 mapping validator (`validate_phase2_mapping.py`).

**Run both:**
```bash
# 1. Validate overall mapping and structure
python3 scripts/validate_phase2_mapping.py

# 2. Validate individual page YAML accuracy
python3 scripts/validate_page_yaml.py
```

## Prevention Tips

### While Cleaning Pages

1. **Always check the mapping first:**
   ```bash
   python3 -c "
   import json
   with open('phase2_corrected_mapping.json') as f:
       mapping = json.load(f)
   entry = mapping[23]  # For page 024
   print(f\"Source: {entry['source_path']}\")
   print(f\"Output: {entry['output_file']}\")
   print(f\"Internal: {entry['internal_page']}\")
   print(f\"Rules: {entry['rules']}\")
   "
   ```

2. **Look for § patterns in source:**
   ```bash
   grep "^§" phase1_ocr/claude/page_NNN.txt
   ```

3. **Set YAML before writing:**
   - `page_number` = sequential output number (from filename)
   - `internal_page` = book's actual page number (from header)
   - `rules_starting` = rules with `§ N.` or `§ N ` in content
   - `rules_continuing` = empty if no rules starting, else list rules from previous

4. **Validate immediately after cleaning each batch:**
   ```bash
   python3 scripts/validate_page_yaml.py
   ```

## Debugging Tips

### Find which page has § N

```bash
grep -l "^§ 27" phase2_cleaned/page_*.md
```

### Check rule distribution

```bash
python3 << 'EOF'
import re, glob

for page in sorted(glob.glob('phase2_cleaned/page_*.md')):
    with open(page) as f:
        content = f.read()
    rules = re.findall(r'^§\s*(\d+)[.\s]', content[content.find('---', 10)+3:], re.MULTILINE)
    if rules:
        print(f"{page.split('/')[-1]}: {rules}")
EOF
```

### Compare YAML vs actual

```bash
python3 << 'EOF'
import re

page = "phase2_cleaned/page_023.md"
with open(page) as f:
    content = f.read()

yaml_rules = re.search(r'rules_starting:\s*(\[.*?\])', content).group(1)
yaml_end = content.find('---', 10)
actual_rules = re.findall(r'^§\s*(\d+)[.\s]', content[yaml_end+3:], re.MULTILINE)

print(f"YAML says: {yaml_rules}")
print(f"Actual has: {actual_rules}")
EOF
```

## Summary

**Always validate after cleaning pages!**

```bash
python3 scripts/validate_page_yaml.py
```

This catches YAML errors before they compound and make Phase 3 extraction fail.
