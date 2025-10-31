# OCR Project Directory Structure

## Planned Clean Organization

```
ocr/
├── README.md                    # Project overview
├── .gitignore                   # Git ignore rules
├── .gitattributes              # Git LFS configuration
├── .env.template               # Environment template
│
├── docs/                        # Documentation
│   ├── STRUCTURING_RAW_OCR.md  # Stage 1-4 specifications
│   ├── PROGRESS.md             # Current status
│   └── DIRECTORY_STRUCTURE.md  # This file
│
├── scripts/                     # All scripts organized by purpose
│   ├── processing/              # OCR processing scripts
│   │   ├── process_batch.py    # Main 3-stage processor
│   │   ├── process_to_50.sh    # Helper for first 50 pages
│   │   └── run_full_processing.sh  # Full automation
│   ├── analysis/                # Review and analysis scripts
│   │   └── review_results.py   # Quality review
│   └── enhancement/             # Future Stage 4 scripts
│       └── enhance_sanskrit.py  # Sanskrit term tagging (TODO)
│
├── data/                        # Runtime data files
│   ├── processing_status.json  # Processing progress
│   └── consistency_data.json   # Cross-page consistency
│
├── logs/                        # Log files
│   └── *.log                   # Processing logs
│
├── source/                      # Original source PDFs
│   └── *.pdf                   # Raw PDF files (Git LFS)
│
├── ocr_output/                  # Raw OCR text
│   ├── claude/                 # Claude OCR output
│   │   ├── page_*.txt          # Text files
│   │   ├── page_*.json         # Metadata
│   │   └── page_*.png          # Page images
│   └── google/                 # Google Vision OCR output
│       ├── page_*.txt
│       └── page_*.png
│
└── structured_pages/            # Phase 2 output: Structured markdown
    ├── page_*.md               # Structured content
    └── page_*_validation.json  # Validation reports

```

## Future Phases (Not Yet Created)

```
├── rules/                       # Phase 3: Assembled rules
│   └── rule_*.md               # Complete rules (multi-page assembly)
│
├── enhanced_pages/              # Phase 4: Sanskrit-enhanced
│   └── page_*.md               # With proper IAST tagging
│
└── final/                       # Final compiled output
    ├── complete_grammar.md     # Single compiled file
    └── metadata/               # Extracted metadata
```

## Current State (During Transition)

Some files are still in root while background processing runs:
- `consistency_data.json` (being written by active process)
- `processing_status.json` (being written by active process)

These will be moved to `data/` once processing completes.

## Notes

- Files match scan page numbers (page_020.md = scan 20)
- `actual_page_number` in metadata = book's printed page number
- Rules may span multiple page files (tracked via `continues_from`/`continues_to`)
- Phase 3 will assemble complete rules from page fragments
