# Kale's Sanskrit Grammar - Digital Edition

OCR digitization and structured extraction of Kale's "A Higher Sanskrit Grammar" (1894).

## Contents

- **966 rules** from Kale's original text, individually extracted
- Clean markdown format with YAML front matter
- IAST transliteration and Devanagari in structured notation
- Automated OCR cleanup pipeline using Claude AI

## Repository Structure

```
├── raw_pages/           # Original OCR text files (729 pages)
├── output/              # Processed markdown (v7)
├── rules/               # Extracted rules (001.md - 972.md)
├── rules_cleaned/       # Claude-cleaned rules (in progress)
├── scripts/             # Processing scripts
│   ├── extract_simple.py
│   ├── process_rules_batch.py
│   └── processing/      # Section extraction scripts
├── MARKDOWN_SPEC.md     # Formatting specification
└── PROCESSING_READY.md  # Processing guide
```

## Extraction Status

✅ **966/966 rules extracted** (6 rule numbers don't exist in original)
🔄 **Claude cleanup in progress** - OCR correction and formatting

## Markdown Format

Each rule file follows this structure:

```markdown
---
rule: §N
---

[Rule content with IAST in @[...] and Devanagari in @deva[...]]
```

### Notation
- **IAST**: `@[saṃskṛta]`, `@[pāṇini]`, `@[guṇa]`
- **Devanagari**: `@deva[संस्कृत]`, `@deva[पाणिनि]`, `@deva[गुण]`

## Processing

Process rules through Claude for cleanup:

```bash
# Test batch
python3 scripts/process_rules_batch.py 1 10

# Process in batches
python3 scripts/process_rules_batch.py 1 100
python3 scripts/process_rules_batch.py 101 200
```

See `PROCESSING_READY.md` for detailed instructions.

## Non-existent Rules

The following rule numbers are skipped in Kale's original:
- §134, §433, §631-632, §635, §637

Total actual rules: **966**

## Source

Kale, M.R. (1894). *A Higher Sanskrit Grammar*. Bombay Education Society's Press.

## License

This is a digitization of a public domain work.
