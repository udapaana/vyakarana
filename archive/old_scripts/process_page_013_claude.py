#!/usr/bin/env python3
"""Process page_013a and page_013b with Claude Vision OCR."""

import base64
import io
import os
from pathlib import Path
from PIL import Image


def encode_image_base64(image: Image.Image) -> str:
    """Encode PIL Image to base64 string for Claude API."""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=95)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def ocr_image_with_claude(image_path: Path, anthropic_client) -> dict:
    """Extract text from image using Claude Vision API.

    Args:
        image_path: Path to image file
        anthropic_client: Anthropic client instance

    Returns:
        Dict with text and usage info
    """
    print(f"Processing {image_path.name}...")

    # Load image
    image = Image.open(image_path)
    image_base64 = encode_image_base64(image)

    # Craft prompt optimized for Sanskrit grammar text
    prompt = """You are doing OCR transcription. Transcribe EVERY SINGLE CHARACTER of text visible in this image exactly as shown.

CRITICAL: Do NOT describe the page. Do NOT summarize. TRANSCRIBE CHARACTER-BY-CHARACTER.

Transcribe ALL text including:
- Sanskrit Devanagari script (धी, भू, सू, प्रधी, etc.)
- English text
- IAST transliteration with diacriticals (ā, ī, ū, ṛ, ṝ, ḷ, ṃ, ḥ, ṅ, ñ, ṭ, ḍ, ṇ, ś, ṣ)
- Section markers (§)
- ALL punctuation marks, quotation marks
- Footnote markers and numbers
- Page numbers

For IAST diacriticals:
- Long vowels: ā, ī, ū (macron above)
- Vocalic r: ṛ, ṝ (dot below)
- Vocalic l: ḷ, ḹ (dot below)
- Nasals: ṃ, ḥ, ṅ, ñ, ṇ
- Retroflexes: ṭ, ḍ, ṇ (dot below)
- Sibilants: ś (acute), ṣ (dot below)

Preserve layout:
- Line breaks
- Indentation
- Tables (use spacing)
- Column structure

Mark uncertain text with [?]

START TRANSCRIPTION NOW - character by character:"""

    # Call Claude API
    print(f"  Calling Claude Vision API...")
    response = anthropic_client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_base64,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    )

    # Extract text from response
    text = ""
    for content_block in response.content:
        if content_block.type == "text":
            text += content_block.text

    print(f"  ✓ Extracted {len(text)} characters")
    print(
        f"  ✓ Tokens: {response.usage.input_tokens} in, {response.usage.output_tokens} out"
    )

    return {
        "text": text,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        },
    }


def main():
    """Process the two images."""
    # Import anthropic
    try:
        import anthropic
    except ImportError:
        print("Error: anthropic package not installed")
        print("Install with: pip install anthropic")
        return 1

    # Load API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        print("Loading API key from .env file...")
        env_file = Path(__file__).parent / ".env"
        if env_file.exists():
            with env_file.open() as f:
                for line in f:
                    if line.startswith("ANTHROPIC_API_KEY="):
                        api_key = line.split("=", 1)[1].strip()
                        break

    if not api_key:
        print("Error: Could not find Anthropic API key")
        return 1

    # Create client
    client = anthropic.Anthropic(api_key=api_key)

    print("Claude Vision OCR - Processing page_013a and page_013b")
    print("=" * 70)
    print()

    # Define paths
    base_dir = Path(__file__).parent
    google_dir = base_dir / "ocr_output/google"

    images = [("page_013a.png", "page_013a.txt"), ("page_013b.png", "page_013b.txt")]

    results = []

    # Process each image
    for img_name, txt_name in images:
        img_path = google_dir / img_name
        txt_path = google_dir / txt_name

        if not img_path.exists():
            print(f"Error: {img_path} not found")
            continue

        try:
            # Run OCR
            result = ocr_image_with_claude(img_path, client)

            # Save text
            with txt_path.open("w", encoding="utf-8") as f:
                f.write(result["text"])

            print(f"  ✓ Saved to {txt_path.name}")
            print()

            results.append(
                {
                    "file": txt_name,
                    "path": txt_path,
                    "char_count": len(result["text"]),
                    "tokens": result["usage"],
                }
            )

        except Exception as e:
            print(f"  ✗ Error: {e}")
            print()
            import traceback

            traceback.print_exc()
            results.append({"file": txt_name, "path": None, "error": str(e)})

    # Print summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for result in results:
        if "error" in result:
            print(f"✗ {result['file']}: ERROR - {result['error']}")
        else:
            print(f"✓ {result['file']}: {result['char_count']} characters")
            print(f"  Path: {result['path']}")
            print(
                f"  Tokens: {result['tokens']['input_tokens']} in, {result['tokens']['output_tokens']} out"
            )

    print()
    return 0


if __name__ == "__main__":
    exit(main())
