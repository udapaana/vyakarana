# Parallel Processing Strategy: Phase 1 + Phase 2 Simultaneously

**Last Updated**: 2025-11-07
**Status**: 📋 **READY TO IMPLEMENT**

---

## Overview

Rather than waiting for Phase 1 (OCR) to fully complete before starting Phase 2 (reconciliation/structuring), we can **process both phases in parallel**:

- **Phase 1**: Continue OCRing appendix pages and remaining sources
- **Phase 2**: Start reconciling/structuring main grammar rules (where OCR is already complete)

This significantly reduces total project time and allows work to proceed on the critical 972 rules immediately.

---

## Page Ranges

### Main Grammar Rules (Priority)
- **Pages 1-542**: Contains all 972 grammar rules (§1 through §972)
- **Status**: OCR mostly complete for DLI_2015
- **Action**: Start Phase 2 processing NOW

### Appendices (Lower Priority)
- **Pages 543-729**: Appendices (Prosody, Dhātukośa)
- **Status**: OCR in progress
- **Action**: Continue Phase 1, process with Phase 2 when ready

---

## Current OCR Status

Let me check what's already available:

```bash
# Check DLI_2015 OCR coverage
ls phase1_ocr/google/page_*.txt | wc -l
ls phase1_ocr/claude/page_*.txt | wc -l

# Check Official_1931 OCR coverage
ls phase1_ocr/images/official_1931/page_*.png | wc -l

# Check xMqc_1931 status
ls phase1_ocr/images/xmqc_1931/page_*.png 2>/dev/null | wc -l
```

Based on prior documentation:
- **DLI_2015**: ✅ 728/729 pages complete (Google + Claude)
- **Official_1931**: ⚙️ Images extracted for 732 pages, OCR in progress
- **xMqc_1931**: 📋 Needs image extraction + OCR

---

## Parallel Processing Plan

### Track 1: Phase 2 Processing (Start Immediately)

**Process pages 1-542** where OCR is already complete:

```bash
# Check which pages in 1-542 range have both Google + Claude OCR
cd /Users/skmnktl/Downloads/ocr

# List available OCR for main rules
python3 scripts/validation/check_ocr_coverage.py \
  --range 1-542 \
  --sources dli_2015 \
  --engines google claude \
  --output ocr_coverage_rules.json
```

**Start Phase 2 v1 (dual-engine) on available pages:**

```bash
# Process main grammar rules (pages 1-542)
python3 scripts/processing/process_batch.py \
  --start-page 1 \
  --end-page 542 \
  --batch-size 10 \
  --output structured_pages
```

**Benefits:**
- Get all 972 rules structured immediately
- Phase 3 (rule extraction) can start sooner
- Main content ready for review while appendices process

### Track 2: Phase 1 OCR Completion (Continue in Background)

**Priority 1: Complete Official_1931 OCR** (for Phase 2 v2 multi-source)

```bash
# Process Official_1931 images with Claude Vision
python3 scripts/claude_vision_ocr.py \
  --source official_1931 \
  --start-page 1 \
  --end-page 732 \
  --output phase1_ocr/sources/official_1931/ \
  --skip-existing
```

**Priority 2: Complete appendix pages (543-729) for DLI_2015**

```bash
# Check if any appendix pages missing
python3 scripts/validation/check_ocr_coverage.py \
  --range 543-729 \
  --sources dli_2015 \
  --engines google claude

# Process any missing appendix pages
python3 scripts/dual_ocr.py \
  --pdf source/candidates/DLI_2015_IGNCA_Delhi.pdf \
  --start 543 \
  --end 729 \
  --google-output phase1_ocr/google \
  --claude-output phase1_ocr/claude \
  --skip-existing
```

**Priority 3: Process xMqc_1931 source** (for Phase 2 v2 multi-source)

```bash
# Extract images
python3 scripts/extract_source_images.py \
  --source xmqc_1931 \
  --start 1 --end 729 \
  --output phase1_ocr/images/xmqc_1931/

# OCR with Claude Vision
python3 scripts/claude_vision_ocr.py \
  --source xmqc_1931 \
  --start-page 1 \
  --end-page 729 \
  --output phase1_ocr/sources/xmqc_1931/
```

### Timeline (Parallel)

| Time | Track 1: Phase 2 (Main Rules) | Track 2: Phase 1 (Appendices + Alt Sources) |
|------|-------------------------------|---------------------------------------------|
| **Hours 0-4** | Process pages 1-100 (batch 1-10) | Start Official_1931 OCR (pages 1-200) |
| **Hours 4-8** | Process pages 101-200 (batch 11-20) | Continue Official_1931 OCR (pages 201-400) |
| **Hours 8-12** | Process pages 201-300 (batch 21-30) | Continue Official_1931 OCR (pages 401-600) |
| **Hours 12-16** | Process pages 301-400 (batch 31-40) | Complete Official_1931 OCR (pages 601-732) |
| **Hours 16-20** | Process pages 401-500 (batch 41-50) | Start DLI appendices OCR (pages 543-600) |
| **Hours 20-24** | Process pages 501-542 (batch 51-55) | Continue DLI appendices (pages 601-700) |
| **Hours 24-28** | **Rules complete! Start Phase 3** | Complete DLI appendices (pages 701-729) |
| **Hours 28-32** | Phase 3: Extract rules 1-200 | Start xMqc_1931 image extraction |
| **Hours 32-36** | Phase 3: Extract rules 201-400 | Start xMqc_1931 OCR (pages 1-200) |
| **Hours 36-40** | Phase 3: Extract rules 401-600 | Continue xMqc_1931 OCR (pages 201-400) |
| **Hours 40-48** | Phase 3: Extract rules 601-972 ✅ | Continue xMqc_1931 OCR (pages 401-729) |
| **Hours 48-52** | **Phase 3 complete!** | Complete xMqc_1931 OCR ✅ |

**Key Milestones:**
- **Hour 24**: All 972 rules structured (Phase 2 v1 complete for rules)
- **Hour 48**: All rules extracted (Phase 3 complete)
- **Hour 52**: All OCR sources complete, ready for Phase 2 v2

---

## Immediate Actions (Next 30 Minutes)

### 1. Verify OCR Coverage for Pages 1-542

```bash
cd /Users/skmnktl/Downloads/ocr

# Create quick check script
cat > check_rules_coverage.sh << 'EOF'
#!/bin/bash
echo "Checking OCR coverage for main grammar rules (pages 1-542)..."
missing_google=0
missing_claude=0

for i in $(seq 1 542); do
    page=$(printf "%03d" $i)

    if [ ! -f "phase1_ocr/google/page_${page}.txt" ]; then
        echo "Missing Google OCR: page $i"
        ((missing_google++))
    fi

    if [ ! -f "phase1_ocr/claude/page_${page}.txt" ]; then
        echo "Missing Claude OCR: page $i"
        ((missing_claude++))
    fi
done

echo ""
echo "Summary:"
echo "  Pages 1-542 (main rules)"
echo "  Missing Google OCR: $missing_google pages"
echo "  Missing Claude OCR: $missing_claude pages"
echo "  Ready for Phase 2: $((542 - missing_google - missing_claude)) pages"
EOF

chmod +x check_rules_coverage.sh
./check_rules_coverage.sh
```

### 2. Start Phase 2 on First Batch

```bash
# Process first 10 pages as test
python3 scripts/processing/process_batch.py \
  --start-page 1 \
  --batch-size 10 \
  --output structured_pages

# Check results
ls structured_pages/page_00*.md
```

### 3. Start Background OCR Processing

**Terminal 1: Phase 2 Processing (foreground)**
```bash
# Process main rules in batches
python3 scripts/processing/process_batch.py \
  --start-page 1 \
  --end-page 542 \
  --batch-size 10
```

**Terminal 2: Phase 1 OCR (background)**
```bash
# Complete Official_1931 OCR in background
nohup python3 scripts/claude_vision_ocr.py \
  --source official_1931 \
  --start-page 1 \
  --end-page 732 \
  --output phase1_ocr/sources/official_1931/ \
  --skip-existing \
  > logs/official_1931_ocr.log 2>&1 &

# Monitor progress
tail -f logs/official_1931_ocr.log
```

---

## Phase 2 Processing Strategy

### Batch Processing Recommendations

**For 542 pages, using batches of 10:**
- Total batches: 55 batches
- Time per batch: ~20-30 minutes (including processing + validation)
- Total time: ~18-27 hours for all main rules

**Optimize processing:**
1. **Parallel batches**: If using Claude Max (no rate limits), can run 2-3 batches in parallel
2. **Overnight processing**: Set up batches to run overnight
3. **Progressive validation**: Review first 50 pages, adjust prompts if needed, then continue

### Quality Checkpoints

**After batch 5 (50 pages):**
- Review validation reports
- Check Sanskrit tagging coverage
- Verify YAML metadata quality
- Adjust prompts if needed

**After batch 10 (100 pages):**
- Spot-check random pages
- Verify consistency data accumulation
- Check for common issues

**After batch 25 (250 pages):**
- Comprehensive quality review
- Verify all 972 rules are being captured correctly
- Check cross-references and citations

---

## Handling Appendices

### When Appendix OCR Completes

Once pages 543-729 have complete OCR:

```bash
# Process appendix pages with Phase 2
python3 scripts/processing/process_batch.py \
  --start-page 543 \
  --end-page 729 \
  --batch-size 10 \
  --output structured_pages
```

### Appendix Structure (Different from Rules)

Appendices have different structure:
- **Appendix I (Prosody)**: Pages ~543-650
  - Meter definitions (samavṛttas, viṣamavṛttas)
  - Tables of metrical patterns
- **Appendix II (Dhātukośa)**: Pages ~651-729
  - Verb root dictionary
  - Root, class, meaning tables

**Note**: May need adjusted prompts for appendix structuring (more tables, less prose)

---

## Phase 2 → Phase 3 Handoff

### As Soon as Pages 1-542 Complete Phase 2

**Start Phase 3 immediately** (no need to wait for appendices):

```bash
# Extract all 972 rules from structured pages
python3 scripts/extraction/extract_rules.py \
  --start 1 \
  --end 972 \
  --input structured_pages \
  --output rules

# Generate table of contents
python3 scripts/extraction/generate_toc.py \
  --rules-dir rules \
  --output TABLE_OF_CONTENTS.md
```

**Phase 3 can run in parallel with:**
- Appendix pages completing Phase 2
- Phase 1 OCR of alternative sources (Official_1931, xMqc_1931)

---

## Benefits of Parallel Processing

### Time Savings
- **Sequential approach**: Phase 1 complete → Phase 2 → Phase 3 = ~80-100 hours
- **Parallel approach**: All phases overlapping = ~50-60 hours
- **Savings**: 30-40 hours (40-50% faster)

### Risk Reduction
- Main content (972 rules) processed and validated earlier
- Issues discovered sooner, can adjust approach
- Critical deliverables ready faster

### Flexibility
- Can start using structured rules immediately
- Don't have to wait for appendices to make progress
- Can deliver Phase 3 output (extracted rules) while Phase 2 v2 is still being planned

### Resource Utilization
- CPU usage optimized (parallel tracks)
- Can work on one track while another processes
- No idle time waiting for sequential completion

---

## Monitoring Progress

### Create Status Dashboard

```bash
# Create monitoring script
cat > monitor_parallel_progress.sh << 'EOF'
#!/bin/bash

echo "=== Parallel Processing Status ==="
echo ""

# Phase 1: OCR Status
echo "Phase 1: OCR Coverage"
echo "  DLI_2015 (Google):    $(ls phase1_ocr/google/page_*.txt 2>/dev/null | wc -l) / 729 pages"
echo "  DLI_2015 (Claude):    $(ls phase1_ocr/claude/page_*.txt 2>/dev/null | wc -l) / 729 pages"
echo "  Official_1931:        $(ls phase1_ocr/sources/official_1931/page_*.txt 2>/dev/null | wc -l) / 732 pages"
echo "  xMqc_1931:            $(ls phase1_ocr/sources/xmqc_1931/page_*.txt 2>/dev/null | wc -l) / 729 pages"
echo ""

# Phase 2: Structured Pages
echo "Phase 2: Structured Pages"
echo "  Rules (1-542):        $(ls structured_pages/page_{001..542}.md 2>/dev/null | wc -l) / 542 pages"
echo "  Appendices (543-729): $(ls structured_pages/page_{543..729}.md 2>/dev/null | wc -l) / 187 pages"
echo "  Total:                $(ls structured_pages/page_*.md 2>/dev/null | wc -l) / 729 pages"
echo ""

# Phase 3: Extracted Rules
echo "Phase 3: Extracted Rules"
echo "  Individual rules:     $(ls rules/rule_*.md 2>/dev/null | wc -l) / 972 rules"
echo ""

# Calculate completion percentages
rules_pct=$(( $(ls structured_pages/page_{001..542}.md 2>/dev/null | wc -l) * 100 / 542 ))
echo "Main Rules Progress: ${rules_pct}%"
EOF

chmod +x monitor_parallel_progress.sh
```

**Run periodically:**
```bash
watch -n 300 ./monitor_parallel_progress.sh  # Update every 5 minutes
```

---

## Rollback / Pause Strategy

### If Issues Arise

**Pause Phase 2 processing:**
```bash
# Stop current batch processing
pkill -f process_batch.py

# Review current status
python3 scripts/processing/process_batch.py --status
```

**Review and adjust:**
1. Check validation reports for error patterns
2. Adjust prompts if needed
3. Reprocess problematic pages
4. Resume from last successful batch

**Phase 1 continues unaffected** - OCR processing is independent

---

## Success Criteria

### Phase 2 (Main Rules) Success
✅ Pages 1-542 structured with 99%+ accuracy
✅ All 972 rules captured in structured pages
✅ YAML metadata complete and valid
✅ Sanskrit terms properly tagged
✅ Ready for Phase 3 extraction

### Phase 1 (All Sources) Success
✅ DLI_2015: 729 pages complete (Google + Claude)
✅ Official_1931: 732 pages complete (Claude)
✅ xMqc_1931: 729 pages complete (Claude)
✅ Ready for Phase 2 v2 multi-source reconciliation

---

## Next Steps

1. ✅ **Verify OCR coverage** for pages 1-542 (run check script)
2. 🚀 **Start Phase 2** on first batch of main rules (pages 1-10)
3. 🔄 **Start Phase 1** background processing for remaining sources
4. 📊 **Monitor progress** with status dashboard
5. ✅ **Review quality** after first 50 pages
6. 🚀 **Continue parallel processing** until all tracks complete

**Ready to start parallel processing NOW!** 🚀

---

## Related Documentation

- [PHASE2_V2_PLAN.md](PHASE2_V2_PLAN.md) - Multi-source reconciliation plan
- [PHASE2_STATUS.md](PHASE2_STATUS.md) - Phase 2 v1 status
- [PIPELINE_OVERVIEW.md](PIPELINE_OVERVIEW.md) - Overall pipeline
- [README.md](../README.md) - Project overview
