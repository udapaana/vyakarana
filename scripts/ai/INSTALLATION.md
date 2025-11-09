# Installation & Setup

Complete setup guide for the Claude AI Wrapper.

## System Requirements

- Python 3.7 or higher
- Internet connection
- Anthropic API key

## Step 1: Check Python Version

```bash
python3 --version
```

Should show: `Python 3.7.0` or higher

## Step 2: Install Dependencies

```bash
# Navigate to project root
cd /Users/skmnktl/Downloads/ocr

# Install required packages
pip install anthropic python-dotenv

# Or if you have a requirements.txt
pip install -r requirements.txt
```

### Package Details

- **anthropic** (>=0.18.0) - Official Anthropic Claude API client
- **python-dotenv** (>=1.0.0) - Environment variable management (optional)

## Step 3: Get API Key

1. Go to https://console.anthropic.com
2. Sign in or create an account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-ant-api03-...`)

## Step 4: Set API Key

### Option A: Environment Variable (Recommended)

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-YOUR_KEY_HERE"
```

To make permanent, add to your shell profile:

```bash
# For bash
echo 'export ANTHROPIC_API_KEY="sk-ant-api03-..."' >> ~/.bashrc
source ~/.bashrc

# For zsh
echo 'export ANTHROPIC_API_KEY="sk-ant-api03-..."' >> ~/.zshrc
source ~/.zshrc

# For fish
echo 'set -x ANTHROPIC_API_KEY "sk-ant-api03-..."' >> ~/.config/fish/config.fish
source ~/.config/fish/config.fish
```

### Option B: .env File

```bash
# In project root
echo 'ANTHROPIC_API_KEY=sk-ant-api03-...' >> .env
```

The wrapper will automatically load from `.env` if `python-dotenv` is installed.

## Step 5: Verify Installation

```bash
# Test imports
python3 -c "from scripts.ai import ClaudeClient; print('✓ Installation successful')"

# Test CLI
python3 -m scripts.ai --help

# Test API connection (optional - uses API credits)
python3 -c "
from scripts.ai import ClaudeClient
client = ClaudeClient()
print('✓ API connection working')
"
```

Expected output:
```
✓ Installation successful
✓ API connection working
```

## Step 6: Verify Data Files

```bash
# Check structured pages exist
ls structured_pages/ | head -5

# Should show: page_001.md, page_002.md, etc.

# Count pages
ls structured_pages/page_*.md | wc -l

# Should show: 729
```

## Troubleshooting

### "No module named 'anthropic'"

```bash
pip install anthropic
```

### "No module named 'scripts.ai'"

Make sure you're in the project root:

```bash
cd /Users/skmnktl/Downloads/ocr
python3 -m scripts.ai --help
```

### "API key not found"

Check environment variable is set:

```bash
echo $ANTHROPIC_API_KEY
```

Should show your API key. If empty, set it:

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

### "Rate limit exceeded"

You've hit your API rate limit. Options:
1. Wait a few minutes and retry
2. Check your plan limits at console.anthropic.com
3. The wrapper automatically retries with backoff

### "structured_pages/ not found"

The Phase 2 output is missing. Either:
1. Run Phase 2 first (see main README.md)
2. Check you're in the correct directory

## Optional: Virtual Environment

Recommended for isolation:

```bash
# Create virtual environment
python3 -m venv .venv

# Activate
source .venv/bin/activate  # bash/zsh
# or
source .venv/bin/activate.fish  # fish

# Install dependencies
pip install anthropic python-dotenv

# Use as normal
python3 -m scripts.ai --help

# Deactivate when done
deactivate
```

## Verify Complete Setup

Run all checks:

```bash
#!/bin/bash
echo "Checking installation..."

# 1. Python version
python3 --version || echo "❌ Python 3 not found"

# 2. API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ API key not set"
else
    echo "✓ API key found"
fi

# 3. Dependencies
python3 -c "import anthropic" 2>/dev/null && echo "✓ anthropic installed" || echo "❌ anthropic not installed"

# 4. Module imports
python3 -c "from scripts.ai import ClaudeClient" 2>/dev/null && echo "✓ scripts.ai working" || echo "❌ scripts.ai not found"

# 5. Data files
if [ -d "structured_pages" ]; then
    count=$(ls structured_pages/page_*.md 2>/dev/null | wc -l)
    echo "✓ structured_pages/ found ($count pages)"
else
    echo "❌ structured_pages/ not found"
fi

echo "Setup check complete!"
```

Save as `check_setup.sh`, make executable, and run:

```bash
chmod +x check_setup.sh
./check_setup.sh
```

## Next Steps

Once installation is complete:

1. [Quick Start Guide](QUICKSTART.md) - Extract your first rule
2. [README](README.md) - Full documentation
3. [Test Suite](test_extraction.py) - Run tests

## Support

Issues? Check:
1. Python version (3.7+)
2. API key is set correctly
3. Dependencies installed
4. Project directory structure intact

For project-specific help, see [main README](../../README.md).
