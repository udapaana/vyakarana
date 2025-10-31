#!/bin/bash
# Process pages 8-50 in batches of 10

cd /Users/skmnktl/Downloads/ocr

echo "Processing pages 8-50..."
echo ""

# Pages 8-17
python3 process_batch.py --batch-size 10 --start-page 8

# Pages 18-27
python3 process_batch.py --batch-size 10 --start-page 18

# Pages 28-37
python3 process_batch.py --batch-size 10 --start-page 28

# Pages 38-47
python3 process_batch.py --batch-size 10 --start-page 38

# Pages 48-50
python3 process_batch.py --batch-size 3 --start-page 48

echo ""
echo "✅ Completed processing to page 50"
python3 process_batch.py --status
