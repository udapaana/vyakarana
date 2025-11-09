# Claude AI Wrapper for Phase 3 Rule Extraction

A modular Claude CLI wrapper for extracting Sanskrit grammar rules from OCR'd pages.

## Features

- **Streaming API Support** - Real-time response output
- **Conversation Management** - Maintain context across calls
- **Batch Processing** - Extract all 972 rules sequentially
- **Cost Tracking** - Monitor token usage and estimated costs
- **Resume from Checkpoint** - Automatic recovery from interruptions
- **Error Handling** - Retry with exponential backoff
- **Rate Limiting** - Automatic handling of API limits

## Architecture

```
scripts/ai/
├── __init__.py           # Package exports
├── client.py             # Core Claude API client
├── conversation.py       # Conversation history manager
├── prompts.py            # Prompt templates
├── batch.py              # Batch processor for 972 rules
├── tracker.py            # Cost and usage tracking
├── cli.py                # Command-line interface
├── test_extraction.py    # Test suite
└── README.md             # This file
```

## Installation

```bash
# Ensure dependencies are installed
pip install anthropic

# Set API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Or add to .env file
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
```

## Usage

### Command Line Interface

```bash
# Extract all 972 rules
python -m scripts.ai extract-all --output rules_llm

# Extract specific range (e.g., first 50 rules)
python -m scripts.ai extract-range 1 50 --output rules_test

# Extract single rule
python -m scripts.ai extract-one 77 --output rules_test

# Interactive chat mode
python -m scripts.ai chat

# Verify extracted rule
python -m scripts.ai verify 77 --rules-dir rules_llm
```

### Python API

```python
from pathlib import Path
from scripts.ai import ClaudeClient, BatchProcessor, CostTracker

# Initialize components
client = ClaudeClient(model="claude-sonnet-4-20250514")
tracker = CostTracker()

processor = BatchProcessor(
    structured_pages_dir=Path("structured_pages"),
    output_dir=Path("rules_llm"),
    client=client,
    tracker=tracker,
)

# Extract all rules
processor.process_batch(start_rule=1, end_rule=972)

# Print statistics
tracker.print_summary()
```

### Single Rule Extraction

```python
from scripts.ai import ClaudeClient, BatchProcessor

processor = BatchProcessor(
    structured_pages_dir=Path("structured_pages"),
    output_dir=Path("rules_test"),
)

# Extract rule 77
result = processor.extract_rule(
    rule_number=77,
    start_page=50,
    max_pages=5,
)

if result.success:
    processor.save_rule(result)
    print(f"Rule 77 ends at page {result.end_page}")
```

### Interactive Chat

```python
from scripts.ai import ClaudeClient, ConversationManager

client = ClaudeClient()
conv = ConversationManager()

# Add messages
conv.add_user_message("What is Sanskrit grammar?")
response = client.chat(messages=conv.get_messages(), stream=True)
conv.add_assistant_message(response)

# Save conversation
conv.save(Path("conversation.json"))
```

## Testing

```bash
# Run test suite
python scripts/ai/test_extraction.py

# This will:
# 1. Test prompt generation
# 2. Test conversation management
# 3. Extract rule 77 as a test
# 4. Extract rules 1-5 as a batch test
```

## Configuration

### Models

Default model: `claude-sonnet-4-20250514`

Available models:
- `claude-sonnet-4-20250514` - Latest Sonnet 4 (recommended)
- `claude-sonnet-3-5-20241022` - Sonnet 3.5

```python
client = ClaudeClient(model="claude-sonnet-4-20250514")
```

### Parameters

```python
client = ClaudeClient(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,       # Max response tokens
    temperature=0.0,        # 0.0 = deterministic
)
```

### Batch Processing Options

```python
processor.process_batch(
    start_rule=1,           # First rule to extract
    end_rule=972,           # Last rule (inclusive)
    progress_callback=None, # Optional progress function
)
```

## Cost Estimation

Current pricing (as of 2024):
- Input: $3 per million tokens
- Output: $15 per million tokens

Estimated costs:
- Single rule: ~$0.02-0.05
- All 972 rules: ~$30-50 (varies by rule complexity)

Track actual costs:

```python
tracker = CostTracker()
# ... process rules ...
tracker.print_summary()
```

## Output Format

Extracted rules are saved as markdown files:

```
rules_llm/
├── rule_001.md
├── rule_002.md
├── ...
├── rule_972.md
├── .checkpoint.json        # For resuming
└── usage_stats.json        # Token usage tracking
```

Each rule file contains:
- YAML front matter with metadata
- Rule number and title
- Complete explanation
- Sanskrit examples (Devanagari + IAST)
- Footnotes and cross-references

## Checkpoint & Resume

The system automatically saves progress after each rule:

```json
{
  "last_rule": 326,
  "last_page": 150,
  "timestamp": 1698765432.0
}
```

If interrupted, simply re-run the same command:

```bash
# Will automatically resume from rule 327
python -m scripts.ai extract-all --output rules_llm
```

## Error Handling

The wrapper handles:
- **Rate limits** - Automatic retry with exponential backoff
- **API errors** - Retry up to 3 times
- **Network issues** - Graceful error messages
- **Invalid responses** - Logged and skipped

Failed rules don't block the batch - the process continues.

## Advanced Usage

### Custom Prompts

```python
from scripts.ai.prompts import PromptTemplates

# Custom extraction prompt
prompt = PromptTemplates.extract_rule(
    rule_number=77,
    pages_content=["page 1", "page 2"],
    start_page=50,
)

# Use with client
client = ClaudeClient()
conv = ConversationManager()
conv.add_user_message(prompt)
response = client.chat(messages=conv.get_messages())
```

### Progress Tracking

```python
def progress_callback(current, total):
    percent = (current / total) * 100
    print(f"Progress: {percent:.1f}%")

processor.process_batch(
    start_rule=1,
    end_rule=972,
    progress_callback=progress_callback,
)
```

### Verification

After extraction, verify rules:

```bash
# Verify specific rule
python -m scripts.ai verify 77 --rules-dir rules_llm

# Or in Python
from scripts.ai.prompts import PromptTemplates

prompt = PromptTemplates.verify_rule(
    rule_number=77,
    extracted_content=open("rules_llm/rule_077.md").read(),
    original_pages=["page content..."],
)
```

## Troubleshooting

### API Key Issues

```bash
# Check API key is set
echo $ANTHROPIC_API_KEY

# Or in Python
import os
print(os.getenv('ANTHROPIC_API_KEY'))
```

### Rate Limits

If you hit rate limits:
1. The wrapper automatically retries with backoff
2. Check your API plan limits at console.anthropic.com
3. Consider adding delays: adjust `time.sleep()` in batch.py

### Empty or Incorrect Extractions

If a rule is extracted incorrectly:
1. Check the source pages exist in `structured_pages/`
2. Verify the rule number in the YAML front matter
3. Re-extract with more pages:

```python
result = processor.extract_rule(
    rule_number=77,
    start_page=50,
    max_pages=10,  # Increase if rule spans many pages
)
```

## Contributing

To modify the extraction logic:

1. **Prompts** - Edit `prompts.py`
2. **Parsing** - Edit `batch.py` `extract_rule()` method
3. **Output format** - Edit `batch.py` `save_rule()` method

## License

Part of the Kale Sanskrit Grammar OCR project.

## References

- [Anthropic Claude API](https://docs.anthropic.com)
- [Phase 3 Extraction Plan](../../EXTRACTION_PLAN.md)
- [Project README](../../README.md)
