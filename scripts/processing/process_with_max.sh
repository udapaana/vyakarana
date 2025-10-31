#!/bin/bash
# Process OCR pages using Claude Code session (Max subscription)
# Usage: ./process_with_max.sh START_PAGE END_PAGE

START_PAGE=${1:-1}
END_PAGE=${2:-726}
REPO_DIR="/Users/skmnktl/Downloads/ocr"

echo "📦 Processing pages $START_PAGE to $END_PAGE using Claude Max"
echo ""

for PAGE in $(seq $START_PAGE $END_PAGE); do
    PAGE_NUM=$(printf "%03d" $PAGE)
    PAGE_NAME="page_$PAGE_NUM"

    CLAUDE_OCR="$REPO_DIR/ocr_output/claude/${PAGE_NAME}.txt"
    GOOGLE_OCR="$REPO_DIR/ocr_output/google/${PAGE_NAME}.txt"
    OUTPUT_FILE="$REPO_DIR/structured_pages/${PAGE_NAME}.md"

    # Skip if already processed
    if [ -f "$OUTPUT_FILE" ]; then
        echo "⏭️  [$PAGE] Skipping (already processed)"
        continue
    fi

    # Check if OCR files exist
    if [ ! -f "$CLAUDE_OCR" ] || [ ! -f "$GOOGLE_OCR" ]; then
        echo "❌ [$PAGE] Missing OCR files"
        continue
    fi

    echo "🔄 [$PAGE] Processing page $PAGE..."

    # Build prompt
    PROMPT="Process page $PAGE of Kale's Sanskrit Grammar OCR.

Your task:
1. RECONCILE the two OCR outputs below (Claude and Google)
2. STRUCTURE into markdown with YAML front matter
3. Follow the style guide rules for Sanskrit tagging, footnotes, emphasis markers

CLAUDE OCR:
\`\`\`
$(cat "$CLAUDE_OCR")
\`\`\`

GOOGLE OCR:
\`\`\`
$(cat "$GOOGLE_OCR")
\`\`\`

OUTPUT FORMAT - Return ONLY JSON:
{
  \"structured_markdown\": \"<full markdown here>\",
  \"validation\": {
    \"content_preserved_percentage\": 98.5,
    \"ocr_corrections_made\": 12
  }
}

Return ONLY the JSON, no explanations."

    # Call Claude Code and capture response
    RESPONSE=$(echo "$PROMPT" | claude --print 2>&1)

    # Check for errors
    if echo "$RESPONSE" | grep -q "rate_limit_error"; then
        echo "❌ [$PAGE] Rate limit hit - stopping"
        exit 1
    fi

    # Extract JSON and save
    echo "$RESPONSE" | python3 -c "
import sys
import json
import re

response = sys.stdin.read()

# Find JSON
match = re.search(r'\{.*\}', response, re.DOTALL)
if not match:
    print('ERROR: No JSON found')
    sys.exit(1)

try:
    data = json.loads(match.group(0))
    markdown = data.get('structured_markdown', '')

    if not markdown:
        print('ERROR: No markdown in response')
        sys.exit(1)

    # Save to file
    with open('$OUTPUT_FILE', 'w', encoding='utf-8') as f:
        f.write(markdown)

    print('✅ Saved')

except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
"

    if [ $? -eq 0 ]; then
        echo "✅ [$PAGE] Success"
    else
        echo "❌ [$PAGE] Failed"
    fi

    # Small delay to avoid overwhelming
    sleep 2
done

echo ""
echo "✅ Batch complete!"
