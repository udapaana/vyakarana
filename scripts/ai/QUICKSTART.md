# Quick Start Guide - Claude AI Wrapper

Get started with Phase 3 rule extraction in 5 minutes.

## Prerequisites

```bash
# 1. Ensure you have Python 3.7+
python3 --version

# 2. Install dependencies
pip install anthropic python-dotenv

# 3. Set your API key
export ANTHROPIC_API_KEY="sk-ant-api03-..."
# Or add to .env file
```

## Quick Test (5 seconds)

Test the CLI is working:

```bash
cd /Users/skmnktl/Downloads/ocr
python3 -m scripts.ai --help
```

Expected output: Command list with extract-all, extract-range, etc.

## Extract Your First Rule (30 seconds)

Extract rule 77 as a test:

```bash
# Create test output directory
mkdir -p rules_test

# Extract rule 77 (starts on page 50)
python3 -m scripts.ai extract-one 77 --output rules_test --start-page 50
```

Expected output:
```
Extracting rule 77...
✓ Rule 77 extracted successfully
  End page: 51
  Output: rules_test/rule_077.md
```

Check the result:

```bash
cat rules_test/rule_077.md
```

## Extract First 10 Rules (2 minutes)

```bash
python3 -m scripts.ai extract-range 1 10 --output rules_test
```

Expected output:
```
Starting extraction: Rules 1-10 (10 rules)
[1/10] Extracting Rule § 1... ✓ (ends at page 8)
[2/10] Extracting Rule § 2... ✓ (ends at page 9)
...
Extraction complete!
```

## Extract All 972 Rules (2-3 hours)

**Note:** This will use ~30-50 API calls and cost approximately $30-50.

```bash
# Extract all rules
python3 -m scripts.ai extract-all --output rules_llm

# The process will:
# - Save checkpoints after each rule
# - Resume automatically if interrupted
# - Track token usage and costs
# - Print progress every rule
```

To monitor progress:

```bash
# In another terminal, watch the output directory
watch -n 5 "ls rules_llm/rule_*.md | wc -l"
```

## Resume from Interruption

If the extraction is interrupted, simply re-run the same command:

```bash
python3 -m scripts.ai extract-all --output rules_llm
```

It will automatically resume from the last checkpoint.

## Check Results

```bash
# Count extracted rules
ls rules_llm/rule_*.md | wc -l

# Should show: 972

# Check for empty files
find rules_llm -name "rule_*.md" -size 0

# Should show: (nothing)

# View usage statistics
cat rules_llm/usage_stats.json
```

## Common Commands

```bash
# Extract specific range
python3 -m scripts.ai extract-range 100 150 --output rules_llm

# Extract single rule with custom starting page
python3 -m scripts.ai extract-one 326 --output rules_llm --start-page 150

# Interactive chat mode
python3 -m scripts.ai chat

# Verify extracted rule
python3 -m scripts.ai verify 77 --rules-dir rules_llm --start-page 50
```

## Troubleshooting

### "ANTHROPIC_API_KEY not set"

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
# Or add to .env file in project root
```

### "No module named 'anthropic'"

```bash
pip install anthropic
```

### "Rate limit exceeded"

The CLI automatically retries with backoff. Wait a few seconds and it will resume.

### Empty or incorrect extraction

Try extracting with more pages:

```bash
python3 -m scripts.ai extract-one 77 --output rules_test --start-page 50
```

Check the source pages exist:

```bash
ls structured_pages/page_050.md
```

## Next Steps

- Read full documentation: [README.md](README.md)
- Review extraction plan: [EXTRACTION_PLAN.md](../../EXTRACTION_PLAN.md)
- Run test suite: `python3 scripts/ai/test_extraction.py`

## Cost Estimate

- Single rule: $0.02-0.05
- 10 rules: $0.20-0.50
- All 972 rules: $30-50

Track actual costs with:

```bash
# During extraction, costs are printed
# After extraction, check usage_stats.json
cat rules_llm/usage_stats.json | grep -A 5 "session_stats"
```

## Support

Issues? Check:
1. API key is set correctly
2. `structured_pages/` directory exists with 729 pages
3. Internet connection is stable
4. Anthropic API status: https://status.anthropic.com

For more help, see [README.md](README.md) or [project docs](../../README.md).
