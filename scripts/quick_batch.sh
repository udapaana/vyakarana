#!/bin/bash
# Quick batch opener - opens next 5 unprocessed pages in Preview
# Usage: ./scripts/quick_batch.sh

cd /Users/skmnktl/Downloads/ocr

OUTPUT_DIR="phase1_ocr/sources/official_1931"
IMAGE_DIR="phase1_ocr/images/official_1931"

# Find next unprocessed pages
PAGES=()
for i in {251..732}; do
    PAGE=$(printf "%03d" $i)
    if [ ! -f "$OUTPUT_DIR/${PAGE}.txt" ]; then
        PAGES+=("$IMAGE_DIR/${PAGE}.png")
        if [ ${#PAGES[@]} -eq 5 ]; then
            break
        fi
    fi
done

if [ ${#PAGES[@]} -eq 0 ]; then
    echo "✅ All pages processed!"
    exit 0
fi

echo "📖 Opening ${#PAGES[@]} images..."
for img in "${PAGES[@]}"; do
    basename "$img"
done

# Open all in Preview at once - they'll be in the same window
open -a Preview "${PAGES[@]}"

echo ""
echo "✨ Images opened in Preview!"
echo "💡 TIP: In Preview, use Cmd+C to copy, then paste into Claude Code"
echo "   Or just drag from Preview window into Claude Code chat"
