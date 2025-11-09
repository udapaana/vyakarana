# Batch OCR Workflow for official_1931

## Current Progress
- **Completed**: Pages 1-250 (34.2%)
- **Remaining**: Pages 251-732 (482 pages, 65.8%)
- **Last Internal Page**: 236

## Fastest Workflow (Recommended)

### Method 1: Direct Image Pasting (FASTEST)
This is the most efficient method with zero API cost.

**Steps:**
1. Run the helper script to see which pages need processing:
   ```bash
   cd /Users/skmnktl/Downloads/ocr
   ./scripts/prepare_batch_for_pasting.sh 251 260
   ```

2. Open Finder to the images directory or drag/drop images 251-260 directly into Claude Code chat

3. Say to Claude: **"Transcribe these pages starting from 251"**

4. Claude will process all images in one batch and create the .txt and .json files

**Advantages:**
- ✅ No API costs
- ✅ Can process 5-10 images per message
- ✅ Fast turnaround
- ✅ Direct visual feedback

**Optimal batch size**: 5-10 images at a time (depending on token budget)

---

### Method 2: Manual OCR Helper Script
If you prefer to prepare batches in advance:

```bash
cd /Users/skmnktl/Downloads/ocr
python3 scripts/batch_manual_ocr.py 251 5
```

This will:
- Check which pages need processing
- Open the images in Preview
- Create a manifest file
- Show you what needs to be done

Then you can paste those specific images into Claude Code.

---

## Processing Estimates

With current token budget (~70k tokens remaining):
- **Per batch**: 5-10 pages (depending on complexity)
- **Per session**: 20-30 pages total
- **Time per page**: ~30-60 seconds
- **Remaining work**: ~17-25 sessions to complete all 482 pages

## File Format

Each page produces 2 files:

**NNN.txt:**
```
[Internal page: XXX]

[Full transcribed content with Devanagari and IAST]
```

**NNN.json:**
```json
{
  "page_number": "NNN",
  "source": "official_1931",
  "content_type": "chapter_description",
  "ocr_method": "claude_interactive",
  "timestamp": "YYYY-MM-DD"
}
```

## Quality Standards
- Exact Devanagari transcription
- Proper IAST diacritics (ā, ī, ū, ṛ, ṃ, ḥ, ś, ṣ, etc.)
- Preserve formatting, headers, section markers
- Include [Internal page: XXX] marker at top

## Next Batches
Suggested batches (5 pages each):
- Batch 5: Pages 251-255
- Batch 6: Pages 256-260
- Batch 7: Pages 261-265
- Batch 8: Pages 266-270
- Continue until page 732

## Quick Commands

**Check progress:**
```bash
ls phase1_ocr/sources/official_1931/*.txt | wc -l
```

**Find next page to process:**
```bash
cd /Users/skmnktl/Downloads/ocr
for i in {251..732}; do
  page=$(printf "%03d" $i)
  if [ ! -f "phase1_ocr/sources/official_1931/${page}.txt" ]; then
    echo "Next page: $i"
    break
  fi
done
```

**Verify continuity:**
```bash
cat phase1_ocr/sources/official_1931/250.txt | head -1
# Should show: [Internal page: 236]
```

## Tips for Efficiency

1. **Process in batches of 5**: Maintains quality while being efficient
2. **Use the helper script**: `prepare_batch_for_pasting.sh` automates setup
3. **Paste multiple images**: Claude can handle 5-10 images per message
4. **Work in sessions**: Do 20-30 pages per session to avoid fatigue
5. **Track progress**: Update MANUAL_AGENTIC_OCR_GUIDE.md after each session

## Troubleshooting

**If images won't paste:**
- Try opening them in Preview first
- Use "Copy" then paste into chat
- Try smaller batches (2-3 images)

**If quality drops:**
- Reduce batch size
- Take breaks between batches
- Double-check Devanagari characters

**If unsure about internal page:**
- Reference the previous page's internal number
- Look for page numbers in the image corners
- Internal pages increment sequentially (usually)
