#!/bin/bash
# Run full batch processing for all remaining pages
# Processes in batches of 10 to manage memory and allow monitoring

cd /Users/skmnktl/Downloads/ocr

echo "🚀 Starting full OCR processing pipeline"
echo "=========================================="
echo ""

# Get initial status
python3 process_batch.py --status

echo ""
echo "Starting batch processing..."
echo "Press Ctrl+C to stop at any time (progress is saved)"
echo ""

# Process in batches of 10 until all done
batch_num=1
while true; do
    echo ""
    echo "================================================"
    echo "  BATCH #$batch_num"
    echo "================================================"

    # Run batch
    python3 process_batch.py --batch-size 10

    # Check if we're done
    status_output=$(python3 process_batch.py --status)
    remaining=$(echo "$status_output" | grep "Remaining:" | awk '{print $2}')

    if [ "$remaining" = "0" ]; then
        echo ""
        echo "🎉 ALL PAGES PROCESSED!"
        break
    fi

    batch_num=$((batch_num + 1))

    # Small pause between batches
    echo ""
    echo "⏸️  Pausing 5 seconds before next batch..."
    sleep 5
done

echo ""
echo "=========================================="
echo "✅ Processing complete!"
python3 process_batch.py --status
