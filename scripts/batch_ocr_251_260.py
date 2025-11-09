#!/usr/bin/env python3
# Batch OCR processor for pages 251-260
# This script displays images for Claude to read

import sys
from pathlib import Path

pages = list(range(251, 260 + 1))

print(f"Ready to process {len(pages)} pages: 251-260")
print("Image paths:")

for page_num in pages:
    img_path = Path(f"phase1_ocr/images/official_1931/{page_num:03d}.png")
    if img_path.exists():
        print(f"  {page_num}: {img_path}")
    else:
        print(f"  {page_num}: MISSING")
