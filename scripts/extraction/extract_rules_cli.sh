#!/bin/bash
# Extract rules using claude CLI to avoid API costs
# Since we're running in Claude Code, claude CLI calls use the same session

set -e

BASE_DIR="/Users/skmnktl/Downloads/ocr"
PAGES_DIR="$BASE_DIR/structured_pages"
OUTPUT_DIR="$BASE_DIR/rules_llm"
SCRIPT_DIR="$BASE_DIR/scripts/extraction"

mkdir -p "$OUTPUT_DIR"

# Track current page position
CURRENT_PAGE=1
RULE_NUM="${1:-1}"
END_RULE="${2:-972}"

echo "Starting extraction from rule $RULE_NUM to $END_RULE"
echo "Current page position: $CURRENT_PAGE"
echo ""

while [ $RULE_NUM -le $END_RULE ]; do
    echo "========================================"
    echo "Extracting Rule $RULE_NUM from page $CURRENT_PAGE"
    echo "========================================"

    # Generate pages content (10 pages at a time)
    PAGES_JSON=$(python "$SCRIPT_DIR/extract_one_rule.py" $RULE_NUM $CURRENT_PAGE 2>/dev/null)

    # Save to temp file
    echo "$PAGES_JSON" > /tmp/current_rule_pages.json

    # Extract the pages content for claude
    PAGES_CONTENT=$(echo "$PAGES_JSON" | python -c "import sys, json; data=json.load(sys.stdin); print(data['pages_content'])")

    # Create prompt for claude CLI
    PROMPT="You are extracting rule § $RULE_NUM from Kale's Sanskrit Grammar.

Here are the pages to analyze:

$PAGES_CONTENT

Please extract rule § $RULE_NUM and return ONLY a JSON object with this structure:
{
  \"rule_content\": \"the complete markdown content for rule § $RULE_NUM, including the ## header\",
  \"end_page\": <the page number where this rule ends>,
  \"source_pages\": [<list of page numbers that contained this rule>],
  \"notes\": \"any observations\"
}

IMPORTANT:
- Include the full rule content with all subsections, examples, notes
- Some pages have combined headers like \"§ 5-6\" but then § 5 and § 6 are separate rules
- Stop when you see the next rule's header (§ $(($RULE_NUM + 1)))
- Return ONLY the JSON, no other text"

    # Call claude CLI and capture output
    RESPONSE=$(echo "$PROMPT" | claude --print 2>/dev/null || true)

    # Parse response to extract JSON
    RULE_JSON=$(echo "$RESPONSE" | python -c "
import sys, json, re
response = sys.stdin.read()
# Try to find JSON in response
json_match = re.search(r'\{.*\}', response, re.DOTALL)
if json_match:
    print(json_match.group(0))
else:
    print('{\"error\": \"Could not parse response\"}')
" || echo '{"error": "Failed to parse"}')

    # Check for errors
    if echo "$RULE_JSON" | grep -q '"error"'; then
        echo "ERROR: Failed to extract rule $RULE_NUM"
        echo "$RULE_JSON"
        echo "Skipping to next rule..."
        CURRENT_PAGE=$((CURRENT_PAGE + 1))
        RULE_NUM=$((RULE_NUM + 1))
        continue
    fi

    # Extract components
    RULE_CONTENT=$(echo "$RULE_JSON" | python -c "import sys, json; print(json.load(sys.stdin)['rule_content'])")
    END_PAGE=$(echo "$RULE_JSON" | python -c "import sys, json; print(json.load(sys.stdin)['end_page'])")
    SOURCE_PAGES=$(echo "$RULE_JSON" | python -c "import sys, json; print(json.load(sys.stdin)['source_pages'])")

    # Write rule file
    RULE_FILE="$OUTPUT_DIR/rule_$RULE_NUM.md"
    cat > "$RULE_FILE" << EOF
---
rule: § $RULE_NUM
source_pages: $SOURCE_PAGES
---

$RULE_CONTENT
EOF

    echo "✓ Extracted rule $RULE_NUM"
    echo "  End page: $END_PAGE"
    echo "  Saved to: $RULE_FILE"
    echo ""

    # Update position for next rule
    CURRENT_PAGE=$END_PAGE
    RULE_NUM=$((RULE_NUM + 1))

    # Progress indicator
    if [ $((RULE_NUM % 10)) -eq 0 ]; then
        PROGRESS=$((($RULE_NUM - $1) * 100 / ($END_RULE - $1 + 1)))
        echo "📊 Progress: $RULE_NUM/$END_RULE ($PROGRESS%)"
        echo ""
    fi
done

echo "✅ Extraction complete!"
echo "Extracted rules $1 to $((RULE_NUM - 1))"
