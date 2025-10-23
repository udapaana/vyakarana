#!/bin/bash
# Process all missing rules in batches with rate limiting

echo "Starting cleanup of all missing rules..."
echo "This will take several hours. Progress is tracked in cleanup_progress.json"
echo ""

# Process in batches of 100 with 2.5s delay between each rule
# That's ~250s per batch = ~4 minutes per 100 rules
# For 788 rules: ~32 minutes total

while true; do
    # Check how many are still missing
    missing=$(python3 << 'EOF'
from pathlib import Path
all_rules = set(range(1, 973))
cleaned = set()
if Path('rules_cleaned').exists():
    for f in Path('rules_cleaned').glob('*.md'):
        cleaned.add(int(f.stem))
print(len(all_rules - cleaned))
EOF
)

    echo "Missing rules: $missing"

    if [ "$missing" -eq 0 ]; then
        echo "All rules cleaned!"
        break
    fi

    echo "Processing next batch (up to 100 rules)..."
    python3 scripts/process_missing.py --delay 2.5 --max 100

    if [ $? -ne 0 ]; then
        echo "Error occurred. Stopping."
        break
    fi

    echo ""
    echo "Batch complete. Pausing 10 seconds before next batch..."
    sleep 10
done

echo ""
echo "Final summary:"
python3 << 'EOF'
from pathlib import Path
import json

# Count cleaned files
all_rules = set(range(1, 973))
cleaned = set()
if Path('rules_cleaned').exists():
    for f in Path('rules_cleaned').glob('*.md'):
        cleaned.add(int(f.stem))

# Load progress
if Path('cleanup_progress.json').exists():
    with open('cleanup_progress.json') as f:
        progress = json.load(f)
else:
    progress = {'completed': [], 'failed': [], 'skipped': []}

print(f"Total cleaned: {len(cleaned)}/972")
print(f"Completed: {len(progress['completed'])}")
print(f"Skipped (placeholders): {len(progress['skipped'])}")
print(f"Failed: {len(progress['failed'])}")

if progress['failed']:
    print(f"\nFailed rules: {progress['failed']}")
EOF
