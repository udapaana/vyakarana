# Phase 1: Multi-Source OCR with Claude Code

## Overview

Process the same content from multiple PDF scans using Claude Code interactively.

## Available Sources

1. **Official_1931** - 732 pages, OCRed version
2. **DLI_2015** - 729 pages, image-based scan  
3. **xMqc_1931** - 729 pages (needs verification)

## Workflow

### Step 1: Extract Images

```bash
cd /Users/skmnktl/Downloads/ocr
python3 scripts/extract_source_images.py --start 1 --end 50
```

Output:
```
phase1_ocr/images/official_1931/page_001.png
phase1_ocr/images/dli_2015/page_001.png
phase1_ocr/images/xmqc_1931/page_001.png
```

### Step 2: Claude Code Interactive OCR

You can ask me to:

**Compare sources for a page:**
```
Show me page 44 from all 3 sources
```

**Transcribe best image:**
```
Transcribe page 44 using the best quality source
```

**Process a range:**
```
Process pages 40-50, comparing sources and using best quality for each
```

## How It Works

1. I read the PNG images directly (no API calls)
2. I can see and compare image quality
3. I transcribe the text from the clearest image
4. We save the result with metadata about which source was used

## Output Structure

```
phase1_ocr/
  images/{source}/page_NNN.png     # Extracted images
  sources/{source}/page_NNN.txt    # OCR transcriptions
  sources/{source}/page_NNN.json   # Metadata
```

## Page Equivalency

Track which pages align across sources in `config/page_equivalency.json`:

```json
{
  "44": {
    "official_1931": 44,
    "dli_2015": 44,
    "xmqc_1931": 45
  }
}
```

## Benefits

- No API costs (Claude Code included)
- Visual quality inspection
- Interactive and flexible
- Direct feedback and iteration

