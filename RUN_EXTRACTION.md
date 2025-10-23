# How to Run the Extraction Yourself

## Prerequisites

Make sure you have `uv` installed (Python environment manager)

## Step 1: Identify Sections

This scans the v7 file and creates `sections_index.json` with all chapter/section/rule locations:

```bash
cd /Users/skmnktl/Downloads/ocr
uv run python scripts/processing/identify_sections_ai.py
```

**Output:** `sections_index.json` (complete document structure)

## Step 2: Extract Files

This reads `sections_index.json` and creates individual .md files:

```bash
uv run python scripts/processing/extract_sections_from_index.py
```

**Output:** `v8_sections/` directory with 922 .md files

## Clean Slate (Optional)

If you want to start fresh:

```bash
rm -rf v8_sections sections_index.json
```

Then run Steps 1 and 2 again.

## What Gets Created

```
v8_sections/
├── 01_chapter_i/
│   ├── 01_the_alphabet/
│   │   ├── s001.md
│   │   ├── s002.md
│   │   └── ...
│   └── 02_rules_of_sandhi/
│       ├── s018.md
│       └── ...
├── 02_chapter_ii/
└── ... (13 chapters total, 922 files)
```

## File Format

Each file has:

```yaml
---
rule: §1
---

#### § 1. [Full rule text...]

[Content including examples, notes, citations]
```

## Scripts

- **`scripts/processing/identify_sections_ai.py`** - Scans v7, detects structure
- **`scripts/processing/extract_sections_from_index.py`** - Extracts individual files

Both are standalone Python scripts that use the v7 file as source.
