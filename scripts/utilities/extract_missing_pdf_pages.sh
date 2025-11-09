#!/bin/bash
# Extract specific PDF pages containing missing rules

# Pages we found:
# PDF 23-24: § 7-10
# Need to find others...

# For now, extract the first missing batch (§ 7-10)
echo "Extracting PDF pages with missing rules..."

OUTPUT_DIR="source/missing_pages"
mkdir -p "$OUTPUT_DIR"

PDF="source/candidates/Official_7th_Edition_1931.pdf"

# Extract pages 23-24 (contains § 7-10)
echo "Extracting pages 23-24 (§ 7-10)..."

# Check if we have pdftk or similar
if command -v pdftk &> /dev/null; then
    pdftk "$PDF" cat 23-24 output "$OUTPUT_DIR/pages_23-24.pdf"
    echo "✓ Extracted using pdftk"
elif command -v gs &> /dev/null; then
    gs -sDEVICE=pdfwrite -dNOPAUSE -dBATCH -dSAFER \
       -dFirstPage=23 -dLastPage=24 \
       -sOutputFile="$OUTPUT_DIR/pages_23-24.pdf" "$PDF"
    echo "✓ Extracted using ghostscript"
else
    echo "❌ Need pdftk or ghostscript to extract pages"
    echo "Install with: brew install pdftk-java"
    exit 1
fi

echo ""
echo "Next: Convert to images for OCR"
echo "  cd $OUTPUT_DIR"
echo "  pdftoppm -png pages_23-24.pdf page"
