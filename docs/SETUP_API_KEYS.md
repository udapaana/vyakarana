# API Keys Setup

This project uses two OCR engines for maximum accuracy:

## 1. Google Cloud Vision API

**Why:** Excellent Devanagari script recognition, handles complex ligatures

**Setup:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable the Vision API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Cloud Vision API"
   - Click "Enable"
4. Create service account credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Download JSON key file
5. Set environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-key.json"
   ```

   Or add to your shell profile (~/.zshrc or ~/.bashrc):
   ```bash
   echo 'export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-key.json"' >> ~/.zshrc
   source ~/.zshrc
   ```

**Pricing:**
- Free tier: 1,000 pages/month
- After that: $1.50 per 1,000 pages
- For 729 pages: ~$1.10 (one-time cost)

## 2. Anthropic Claude API

**Why:** Excellent for mixed scripts (English + IAST), table recognition, context understanding

**Setup:**

1. Get API key from [Anthropic Console](https://console.anthropic.com/)
2. Set environment variable:
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```

   Or add to shell profile:
   ```bash
   echo 'export ANTHROPIC_API_KEY="your-key"' >> ~/.zshrc
   source ~/.zshrc
   ```

**Pricing:**
- Claude 3.5 Sonnet: $3 per million input tokens
- Images count as ~1,600 tokens each at 300 DPI
- For 729 pages: ~$3.50 (estimate)

## 3. Install Python Dependencies

```bash
source .venv/bin/activate
pip install google-cloud-vision anthropic
```

## 4. Verify Setup

```bash
# Test Google Vision
python3 scripts/test_google_vision.py

# Test Claude Vision
python3 scripts/test_claude_vision.py
```

## Total Cost Estimate

For processing all 729 pages:
- Google Vision: ~$1.10
- Claude Vision: ~$3.50
- **Total: ~$4.60** (one-time cost for high-quality OCR)

This is significantly cheaper than manual transcription and gives us two independent OCR results to merge for maximum accuracy!
