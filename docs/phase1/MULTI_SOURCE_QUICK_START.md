# Multi-Source OCR Quick Start

## Setup (One Time)

1. **Extract images from all sources:**
   ```bash
   python3 scripts/extract_source_images.py --start 1 --end 729
   ```

2. **Verify sources config:**
   ```bash
   cat config/sources.json
   ```

## Usage with Claude Code

### Compare Sources

```
Show me page 100 from all sources and tell me which has best quality
```

### Transcribe Single Page

```
Transcribe page 100 using the best quality source
```

### Batch Process

```
Process pages 100-150:
1. Compare all sources for each page
2. Use best quality image
3. Save transcription and note which source was used
```

### Check Progress

```
How many pages have we processed from each source?
```

### Build Page Mapping

```
Compare pages 50-60 across sources and build the page equivalency mapping
```

## Directory Structure

```
phase1_ocr/
├── images/                    # Extracted from PDFs
│   ├── official_1931/
│   │   └── page_*.png
│   ├── dli_2015/
│   │   └── page_*.png
│   └── xmqc_1931/
│       └── page_*.png
│
└── sources/                   # OCR outputs
    ├── official_1931/
    │   ├── page_*.txt
    │   └── page_*.json
    ├── dli_2015/
    │   └── page_*.txt
    └── xmqc_1931/
        └── page_*.txt
```

## Config Files

- `config/sources.json` - Source PDFs metadata
- `config/page_equivalency.json` - Page-to-page mapping

## Example Session

```
User: Extract images for pages 1-10 from all sources
Claude: [runs extract script]

User: Show me page 5 from all sources
Claude: [displays 3 images, notes quality differences]

User: Transcribe page 5 from dli_2015 (looks clearest)
Claude: [transcribes and saves to phase1_ocr/sources/dli_2015/page_005.txt]

User: Do this for pages 1-10, picking best source each time
Claude: [processes all pages, saves results]
```

## Next Steps

After Phase 1 multi-source OCR, outputs feed into Phase 2 for structuring and markdown conversion.

