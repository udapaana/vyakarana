#!/bin/bash
# Process overlapping chunks with Claude to extract structured chapters

set -e

# Parse arguments
START_CHUNK=1
END_CHUNK=999999
SKIP_EXISTING=true

while [[ $# -gt 0 ]]; do
    case $1 in
        --start)
            START_CHUNK="$2"
            shift 2
            ;;
        --end)
            END_CHUNK="$2"
            shift 2
            ;;
        --no-skip)
            SKIP_EXISTING=false
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--start N] [--end N] [--no-skip]"
            echo "  --start N    Start from chunk N (default: 1)"
            echo "  --end N      End at chunk N (default: all)"
            echo "  --no-skip    Reprocess existing chunks (default: skip existing)"
            exit 1
            ;;
    esac
done

# Configuration
CHUNKS_DIR="chunks"
OUTPUT_DIR="structured_chapters"
BACKUP_DIR="backups"

# Claude prompt for chunk processing (2-page chunks)
CLAUDE_PROMPT="Fix OCR errors in this 2-page chunk from Kale's 'A Higher Sanskrit Grammar' (1931).

PRESERVE ALL CONTENT - every word, example, footnote, rule.

Fix:
1. OCR typos and spacing
2. Tag Sanskrit: @[term]
3. Diacritics: ā, ī, ū, ṛ, ṃ, ḥ, ñ, ṭ, ḍ, ṇ, ś, ṣ
4. Remove stray characters

OUTPUT ONLY the cleaned text. No markers, no explanations."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check Claude CLI
if ! command -v claude &> /dev/null; then
    log_error "Claude CLI not found"
    exit 1
fi

# Check chunks directory
if [ ! -d "$CHUNKS_DIR" ]; then
    log_error "Directory $CHUNKS_DIR not found. Run create_chunks.py first."
    exit 1
fi

# Count chunks
CHUNK_COUNT=$(find "$CHUNKS_DIR" -name "chunk_*.txt" | wc -l | tr -d ' ')
if [ "$CHUNK_COUNT" -eq 0 ]; then
    log_error "No chunk files found in $CHUNKS_DIR"
    exit 1
fi

log_info "Found $CHUNK_COUNT chunk(s) total"
log_info "Processing chunks $START_CHUNK to $END_CHUNK"
if [ "$SKIP_EXISTING" = true ]; then
    log_info "Skipping already processed chunks"
fi

# Create directories
mkdir -p "$OUTPUT_DIR"
mkdir -p "$BACKUP_DIR"

PROCESSED=0
FAILED=0
SKIPPED=0

# Process each chunk
for chunk_file in "$CHUNKS_DIR"/chunk_*.txt; do
    filename=$(basename "$chunk_file")

    # Extract chunk number
    chunk_num=$(echo "$filename" | sed -E 's/chunk_0*([0-9]+)_.*/\1/')

    # Skip if outside range
    if [ "$chunk_num" -lt "$START_CHUNK" ] || [ "$chunk_num" -gt "$END_CHUNK" ]; then
        continue
    fi

    output_file="$OUTPUT_DIR/${filename%.txt}_structured.md"

    # Skip if already exists (unless --no-skip specified)
    if [ "$SKIP_EXISTING" = true ] && [ -f "$output_file" ]; then
        log_info "Skipping: $filename (already processed)"
        ((SKIPPED++))
        continue
    fi

    log_info "Processing: $filename"

    # Run Claude
    if cat "$chunk_file" | claude --print "$CLAUDE_PROMPT" > "$output_file" 2>/dev/null; then
        log_success "Processed: $filename → ${filename%.txt}_structured.md"
        ((PROCESSED++))
    else
        log_error "Failed: $filename"
        ((FAILED++))
    fi

    echo ""
done

echo "===================="
echo "Cleanup Summary"
echo "===================="
log_success "Processed: $PROCESSED"
if [ $SKIPPED -gt 0 ]; then
    log_info "Skipped: $SKIPPED (already done)"
fi
if [ $FAILED -gt 0 ]; then
    log_error "Failed: $FAILED"
fi

echo ""
log_info "Next steps:"
echo "  1. Review structured outputs in $OUTPUT_DIR/"
echo "  2. Extract individual chapters from structured files"
echo "  3. Deduplicate chapters that appear in overlapping chunks"
echo ""
log_warning "Note: Overlapping chunks may produce duplicate chapters."
log_info "Use the chapter deduplication script to merge them."
