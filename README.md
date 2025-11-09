# Kale's Sanskrit Grammar - OCR Digitization Project

High-quality OCR extraction and structuring of Kale's Higher Sanskrit Grammar (7th Edition, 1931) using dual OCR engines and multi-phase processing pipeline.

## Overview

This project digitizes and structures Kale's Higher Sanskrit Grammar through a comprehensive 4-phase pipeline:

- **Phase 1: Raw OCR** - Dual-engine extraction (Google Vision + Claude Vision)
- **Phase 2: Structuring** - Page-level markdown with metadata
- **Phase 3: Working Files** - Individual rule extraction with complete metadata
- **Phase 4: Production-Ready** - Clean, validated content for publication

**Result:** 955 complete grammar rules + 14 appendix sections with proper Sanskrit tagging, metadata, and cross-references.

## Current Status

### Phase 1: Raw OCR ✅ Complete

- ✅ Dual OCR pipeline: Google Vision (Devanagari) + Claude Vision (IAST diacritics)
- ✅ 729 pages processed from DLI source
- ✅ 732 pages processed from Official 1931 source
- ✅ Image preprocessing (deskew, contrast, noise reduction)
- ✅ Output: `phase1_ocr/sources/` with raw OCR text files

### Phase 2: Structuring ✅ Complete

- ✅ OCR reconciliation (character-by-character comparison)
- ✅ Page-level markdown with YAML frontmatter
- ✅ Standardized formatting (rule numbers, emphasis, footnotes)
- ✅ Output: `phase2_structured/` with 729 structured markdown files

### Phase 3: Rule Extraction ✅ Complete

- ✅ 972 individual rules extracted as `rule_001.md` through `rule_972.md`
- ✅ Rich YAML metadata (chapters, sections, topics, cross-references)
- ✅ Sanskrit word indexing with @deva[] and @[] tags
- ✅ Pāṇini reference linking
- ✅ 14 appendix sections extracted (prosody fundamentals)
- ✅ Complete schema standardization
- ✅ Output: `phase3_rules/` + `phase3_appendix/`

### Phase 4: Production-Ready ✅ Complete

- ✅ 955 production-ready rules (98.25% of 972 total)
- ✅ 17 stub rules removed (table continuations + missing from OCR)
- ✅ 14 appendix sections with proper Sanskrit tagging
- ✅ All files validated with new schema format
- ✅ Clean content ready for publication
- ✅ Output: `phase4_rules/` + `phase4_appendix/`

See [PHASE4_README.md](PHASE4_README.md) and [APPENDIX_README.md](APPENDIX_README.md) for detailed documentation.

## Repository Structure

```
├── phase1_ocr/                          # Phase 1: Raw OCR extraction
│   ├── sources/
│   │   ├── dli_2015/                    # DLI source (729 pages)
│   │   └── official_1931/               # Official 1931 source (732 pages)
│   └── images/                          # Extracted page images
├── phase2_structured/                   # Phase 2: Structured markdown
│   └── page_NNN.md                      # 729 structured pages
├── phase3_rules/                        # Phase 3: Individual rules
│   ├── rule_001.md through rule_972.md  # All 972 rules
│   └── [includes 17 stubs for reference]
├── phase3_appendix/                     # Phase 3: Appendix sections
│   └── appendix_001.md through _014.md  # 14 prosody sections
├── phase4_rules/                        # Phase 4: Production-ready
│   └── rule_001.md through rule_972.md  # 955 complete rules
├── phase4_appendix/                     # Phase 4: Production appendix
│   └── appendix_001.md through _014.md  # 14 transformed sections
├── phase4_images/                       # Phase 4: Unified images
│   └── images/NNN.png                   # Page images for production
├── scripts/                             # Processing scripts
│   ├── ai/                              # AI-assisted extraction
│   ├── extraction/                      # Rule extraction tools
│   ├── processing/                      # Batch processing
│   └── utilities/                       # Helper scripts
├── docs/                                # Documentation
│   ├── README.md                        # Detailed documentation
│   └── README_EXTRACTION.md             # Extraction methodology
├── PHASE4_README.md                     # Phase 4 documentation
├── APPENDIX_README.md                   # Appendix documentation
└── README.md                            # This file
```

## Content Summary

### Grammar Rules (955 complete)

**Chapter Organization:**
- I. The Alphabet (§ 1-34)
- II. Euphonic Combination (Sandhi) (§ 35-71)
- III. Declension of Nouns (§ 73-178)
- IV. Formation of Feminine Bases (§ 179-195)
- V. Declension of Pronouns (§ 196-221)
- VI. Numerals (§ 222-241)
- VII. Formation of Compound Words (§ 242-303)
- VIII. Conjugation of Verbs (§ 304-433)
- IX. Conjugation of Secondary Conjugations (§ 434-487)
- X. Indeclinables (§ 488-500)
- XI. Formation of Nouns (§ 501-603)
- XII. Formation of Participles and Gerunds (§ 604-629)
- XIII. Accents (§ 630-672)
- XIV. Vedic Grammar (§ 673-807)
- XV. Syntax (§ 808-972)

**Missing Rules:** 17 total (1.75%)
- 6 table continuations (not real § sections)
- 11 rules not found in OCR sources

### Appendix (14 sections complete)

**Prosody Fundamentals:**
- § 1-6: Basic concepts (prose/verse, syllables, gaṇas)
- § 7-10: Metre classification (vṛtta, jāti, samavṛtta)
- § 11-12: Caesura and scope
- § 13-14: Common metres (Anuṣṭubh, Āryā)

All sections include proper Sanskrit tagging with @deva[] Devanagari and @[] IAST transliteration.

## OCR Pipeline

### Dual-Engine Strategy

- **Google Cloud Vision API** - Superior Devanagari script recognition (धी, भू, सू)
- **Claude Vision API** - Superior IAST diacriticals (ā, ī, ū, ṛ, ṃ, ḥ, ṭ, ḍ, ṇ, ś, ṣ)
- **Character-by-character reconciliation** - Best readings from both engines
- **Multi-source validation** - Cross-reference multiple PDF scans

### Processing Phases

1. **Image Preprocessing** - Deskew, denoise, enhance contrast
2. **Dual OCR Extraction** - Google + Claude on same preprocessed image
3. **Character Reconciliation** - Compare and select best readings
4. **Metadata Extraction** - YAML frontmatter with rich metadata
5. **Rule Structuring** - Individual files with proper schema
6. **Production Validation** - Clean, validated content only

## Schema Format

All rules use standardized YAML frontmatter:

```yaml
---
rule: § NNN
title: "Rule Title"
page: NNN
source_pages:
  dli: [NNN]
  official_1931: [NNN]
chapter: Chapter Name
section: section-name
subsections: [subsection1, subsection2]
topics: [topic1, topic2]
word_index:
  - Sanskrit term
panini_refs:
  - "Pāṇ. X.Y.Z"
cross_refs:
  - "§ NNN"
confidence: high|medium|low
image: /images/NNN.png
---

## § NNN. Rule Title

Rule content with @deva[देवनागरी] @[IAST] tagging...
```

## Quick Start

### View Production Content

```bash
# Browse production rules
ls phase4_rules/

# View specific rule
cat phase4_rules/rule_001.md

# Browse appendix
ls phase4_appendix/

# View documentation
cat PHASE4_README.md
cat APPENDIX_README.md
```

### Run Scripts

See [scripts/README.md](scripts/README.md) for detailed script documentation.

```bash
# Setup environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run extraction (example)
python3 scripts/extract_all_remaining.py

# Convert schema format (example)
python3 scripts/convert_all_old_schema.py
```

## Statistics

| Metric | Count |
|--------|-------|
| Total rules defined | 972 |
| Complete rules (Phase 4) | 955 (98.25%) |
| Missing rules | 17 (1.75%) |
| Appendix sections | 14 (100%) |
| Total pages processed | 729 (DLI) + 732 (Official) |
| OCR confidence | 99%+ |

## Documentation

- [PHASE4_README.md](PHASE4_README.md) - Phase 4 production documentation
- [APPENDIX_README.md](APPENDIX_README.md) - Appendix structure and content
- [scripts/README.md](scripts/README.md) - Script documentation
- [docs/README.md](docs/README.md) - Detailed methodology

## Source Material

**Primary Sources:**
- Digital Library of India 2015.105411 (729 pages)
- Official 7th Edition 1931 scan (732 pages)

**Edition:** 7th Edition (1931) - Final edition by M.R. Kale
**Publisher:** Gopal Narayen & Co., Bombay

## Cost Analysis

- **Google Vision:** ~$1.09 per source (729 pages)
- **Claude Vision:** ~$12-15 per source (729 pages)
- **Total per source:** ~$13.85 one-time cost
- **Total project:** ~$30 for dual-source processing
- **Quality:** 99%+ accuracy worth the investment

## License

This project digitizes a public domain work (Kale's Sanskrit Grammar, 1931) for preservation and accessibility.

## References

- Kale, M.R. (1931). _A Higher Sanskrit Grammar_. 7th Edition. Gopal Narayen & Co., Bombay.
- Digital Library of India: 2015.105411
- Google Cloud Vision API: https://cloud.google.com/vision
- Anthropic Claude API: https://anthropic.com
