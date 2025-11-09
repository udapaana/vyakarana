# Appendix - Prosody

## Phase Organization

### Phase 1 (Raw OCR)
- **Location**: `phase1_appendix/`
- **Content**: `prosody_complete.md` (raw OCR extraction)
- **Status**: Original OCR with corrupted Devanagari

### Phase 2 (Structured)
- **Location**: `phase2_appendix/`
- **Content**: `prosody_complete.md` (structured single file)
- **Status**: Organized but not split

### Phase 3 (Enumerated Sections)
- **Location**: `phase3_appendix/`
- **Content**: 14 individual section files
- **Format**: `appendix_001.md` through `appendix_014.md`
- **Status**: Split into enumerated sections with basic schema

### Phase 4 (Production-Ready)
- **Location**: `phase4_appendix/`
- **Content**: 14 production-ready section files
- **Format**: `appendix_001.md` through `appendix_014.md`
- **Status**: Clean content with proper Sanskrit tagging

## Appendix Sections (§ 1-14)

| § | File | Title | Topics |
|---|------|-------|--------|
| 1 | appendix_001.md | Poetical Composition | गद्य, पद्य |
| 2 | appendix_002.md | Prosody Definition | Versification basics |
| 3 | appendix_003.md | Stanza Structure (Pāda) | पाद, अक्षर, मात्रा |
| 4 | appendix_004.md | Light and Heavy Syllables | लघु, गुरु |
| 5 | appendix_005.md | Last Syllable of Pāda | Metrical flexibility |
| 6 | appendix_006.md | Gaṇas (Syllabic Feet) | म, न, भ, य, ज, त, र, स |
| 7 | appendix_007.md | Mātrā-Based Metres | जाति, मात्रा-गण |
| 8 | appendix_008.md | Vṛtta and Jāti | वृत्त, जाति classification |
| 9 | appendix_009.md | Classification of Vṛttas | समवृत्त, अर्धसमवृत्त, विषमवृत्त |
| 10 | appendix_010.md | Classes of Samavṛttas | 26 classes by syllable count |
| 11 | appendix_011.md | Yati (Caesura) | यति, pause in verse |
| 12 | appendix_012.md | Scope of Present Treatment | Common metres only |
| 13 | appendix_013.md | Anuṣṭubh/Śloka Metre | अनुष्टुभ्, श्लोक |
| 14 | appendix_014.md | Mātrā-Based Metres Overview | आर्या and variations |

## Transformations Applied

### 1. Sanskrit Tagging
All Sanskrit terms now properly tagged:
- Before: `युयू` (corrupted OCR)
- After: `@deva[पद्य] @[padya]`

### 2. Metadata
All sections have complete YAML frontmatter:
```yaml
appendix: § X
title: "Section Title"
page: XXX
source_pages:
  dli: [XXX]
  official_1931: [XXX]
image: /images/XXX.png
```

### 3. Footnotes
Properly associated with correct sections:
- § 1: (no footnote - introductory)
- § 3: Dandin Kāv. Pr. quote (†)
- § 4: Vowel classification (‡)

### 4. Content Cleaning
- Removed corrupted Devanagari
- Added proper IAST transliteration
- Fixed gaṇa schemes with symbols (∪ for short, — for long)
- Preserved metrical notation accurately

## Statistics

| Metric | Count |
|--------|-------|
| Total sections | 14 |
| With Sanskrit tagging | 14 (100%) |
| With page numbers | 14 (100%) |
| With image references | 14 (100%) |
| Production-ready | 14 (100%) |

## Schema Format

```yaml
---
appendix: § X
title: "Section Title"
section: appendix-prosody
page: XXX
source_pages:
  dli: [XXX]
  official_1931: [XXX]
chapter: Appendix
section_type: prosody

hierarchy:
  chapter: Appendix
  section: Prosody

topics: [prosody, versification, metres]
confidence: high
image: /images/XXX.png
---
```

## Key Concepts Covered

### Fundamental Terms
- **गद्य** (gadya): Prose
- **पद्य** (padya): Verse
- **पाद** (pāda): Quarter of a stanza (line)
- **अक्षर** (akṣara): Syllable
- **मात्रा** (mātrā): Syllabic instant (unit of time)
- **लघु** (laghu): Light syllable
- **गुरु** (guru): Heavy syllable

### Metrical Units
- **गण** (gaṇa): Syllabic foot (group of 3 syllables)
- **मात्रा-गण** (mātrā-gaṇa): Mātrā foot (group of 4 mātrās)

### Metre Types
- **वृत्त** (vṛtta): Syllable-regulated metre
- **जाति** (jāti): Mātrā-regulated metre
- **समवृत्त** (samavṛtta): Regular metre (all pādas alike)
- **अर्धसमवृत्त** (ardhasamavṛtta): Semi-regular (alternate pādas alike)
- **विषमवृत्त** (viṣamavṛtta): Irregular (all pādas different)

## Next Steps

The 14 fundamental sections are complete. The original `prosody_complete.md` contains additional detailed metre descriptions (Indravajrā, Upendravajrā, Vasantatilakā, etc.) that could be extracted as additional enumerated sections if needed.
