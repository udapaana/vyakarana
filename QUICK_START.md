# Quick Start Guide

## Step 1: Get Google Cloud Vision Credentials

You're creating an API key, but for Google Vision we actually need a **Service Account JSON file**.

### Option A: Use API Key (Simpler but less secure)
The API key you just created can work, but we need to modify our code slightly.

### Option B: Use Service Account (Recommended)
1. In Google Cloud Console, go to "IAM & Admin" > "Service Accounts"
2. Click "Create Service Account"
3. Name it "ocr-kale-vision"
4. Grant role: "Cloud Vision API User"
5. Click "Create Key" > "JSON"
6. Download the JSON file
7. Save it somewhere safe (e.g., `~/credentials/google-vision-ocr-kale.json`)
8. In `.env`, set:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=/Users/yourusername/credentials/google-vision-ocr-kale.json
   ```

## Step 2: Get Anthropic API Key

1. Go to https://console.anthropic.com/
2. Create an API key
3. Copy the key
4. In `.env`, set:
   ```
   ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
   ```

## Step 3: Verify Setup

```bash
source .venv/bin/activate
python3 scripts/load_env.py
```

Should show:
```
✓ ANTHROPIC_API_KEY: sk-ant-...
✓ GOOGLE_APPLICATION_CREDENTIALS: /path/to/file.json
✓ All API keys configured!
```

## Step 4: Test OCR

```bash
# Test Google Vision
python3 scripts/google_vision_ocr.py

# Test Claude Vision
python3 scripts/claude_vision_ocr.py
```

## Next Steps

Once both work, we can:
1. Implement the merge module
2. Create the orchestration script
3. Process all 729 pages!
