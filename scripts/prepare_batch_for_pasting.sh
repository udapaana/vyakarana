#!/bin/bash
# Helper script to prepare a batch of images for easy access
# Usage: ./prepare_batch_for_pasting.sh 251 255

START=$1
END=$2

if [ -z "$START" ] || [ -z "$END" ]; then
    echo "Usage: ./prepare_batch_for_pasting.sh START_PAGE END_PAGE"
    echo "Example: ./prepare_batch_for_pasting.sh 251 255"
    exit 1
fi

IMAGE_DIR="phase1_ocr/images/official_1931"
OUTPUT_DIR="phase1_ocr/sources/official_1931"

echo "=========================================="
echo "Batch Preparation: Pages $START-$END"
echo "=========================================="
echo ""

# Check which pages need processing
PAGES_TO_PROCESS=()
for ((i=START; i<=END; i++)); do
    PAGE=$(printf "%03d" $i)
    TXT_FILE="$OUTPUT_DIR/${PAGE}.txt"

    if [ -f "$TXT_FILE" ]; then
        echo "⊘  Page $i: Already processed"
    else
        PAGES_TO_PROCESS+=($i)
        echo "✓  Page $i: Ready to process"
    fi
done

if [ ${#PAGES_TO_PROCESS[@]} -eq 0 ]; then
    echo ""
    echo "All pages already processed!"
    exit 0
fi

echo ""
echo "=========================================="
echo "Images to paste into Claude Code:"
echo "=========================================="
for page in "${PAGES_TO_PROCESS[@]}"; do
    PAGE=$(printf "%03d" $page)
    echo "  $IMAGE_DIR/${PAGE}.png"
done

echo ""
echo "=========================================="
echo "INSTRUCTIONS:"
echo "=========================================="
echo "1. Open Finder and navigate to:"
echo "   $PWD/$IMAGE_DIR"
echo ""
echo "2. Select these images:"
for page in "${PAGES_TO_PROCESS[@]}"; do
    PAGE=$(printf "%03d" $page)
    echo "   - ${PAGE}.png"
done
echo ""
echo "3. Drag and drop them into Claude Code chat"
echo "   OR copy them and paste into the chat"
echo ""
echo "4. Tell Claude: 'Transcribe these pages'"
echo "=========================================="

# Optionally open Finder to the directory
read -p "Open Finder to image directory? (y/n): " OPEN_FINDER
if [ "$OPEN_FINDER" = "y" ]; then
    open "$IMAGE_DIR"
fi
