#!/usr/bin/env python3
"""Claude Vision OCR module for Sanskrit text extraction.

Claude Vision is excellent for:
- Mixed scripts (English + IAST + Devanagari)
- Complex table structures
- Diacritical marks in IAST transliteration
- Understanding context and layout

Following coding standards:
- Deep module: Simple ocr_image() interface, complex API calls hidden
- Dependency injection: Pass in Anthropic client rather than hardcoding
- Comments explain why: Why Claude for IAST, why certain prompts
"""

import base64
import io
from pathlib import Path
from typing import Optional, Dict, Any
from PIL import Image


def encode_image_base64(image: Image.Image) -> str:
    """Encode PIL Image to base64 string for Claude API.

    Why base64: Claude API accepts images as base64-encoded strings.
    """
    buffered = io.BytesIO()
    # Why JPEG: Smaller size, Claude handles compression well
    image.save(buffered, format="JPEG", quality=95)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


def ocr_image_with_claude(
    image: Image.Image,
    anthropic_client: Optional[Any] = None,
    model: str = "claude-3-5-sonnet-20241022"
) -> Dict[str, Any]:
    """Extract text from image using Claude Vision API.

    Why Claude Vision:
    - Excellent at distinguishing IAST diacriticals (ā, ī, ṛ, ṃ, etc.)
    - Understands mixed scripts and layout
    - Can handle complex table structures in appendices
    - Provides context-aware OCR

    Args:
        image: PIL Image object to OCR
        anthropic_client: Anthropic client (injected dependency)
        model: Claude model to use

    Returns:
        Dict containing:
            - 'text': Extracted text
            - 'raw_response': Full Claude response
            - 'model': Model used
    """
    # Lazy import to avoid requiring API key when module is imported
    try:
        import anthropic
    except ImportError:
        raise ImportError(
            "anthropic package not installed. "
            "Install with: pip install anthropic"
        )

    # Create client if not provided (dependency injection)
    if anthropic_client is None:
        anthropic_client = anthropic.Anthropic()

    # Encode image
    image_base64 = encode_image_base64(image)

    # Craft prompt optimized for Sanskrit grammar text
    # Why this prompt: Specific instructions improve accuracy for our use case
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
    response = anthropic_client.messages.create(
        model=model,
        max_tokens=4096,  # Why 4096: Enough for a full page of dense text
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
                    {
                        "type": "text",
                        "text": prompt
                    }
                ],
            }
        ],
    )

    # Extract text from response
    text = ""
    for content_block in response.content:
        if content_block.type == "text":
            text += content_block.text

    return {
        'text': text,
        'model': model,
        'usage': {
            'input_tokens': response.usage.input_tokens,
            'output_tokens': response.usage.output_tokens,
        },
        'raw_response': response
    }


def ocr_page_file(
    image_path: Path,
    output_path: Optional[Path] = None,
    anthropic_client: Optional[Any] = None
) -> Dict[str, Any]:
    """OCR an image file and optionally save results.

    Args:
        image_path: Path to image file
        output_path: Optional path to save OCR results
        anthropic_client: Optional injected Anthropic client

    Returns:
        OCR results dictionary
    """
    import json

    # Load image
    image = Image.open(image_path)

    # Run OCR
    result = ocr_image_with_claude(image, anthropic_client)

    # Save if requested
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save plain text
        txt_path = output_path.with_suffix('.txt')
        with txt_path.open('w', encoding='utf-8') as f:
            f.write(result['text'])

        # Save metadata as JSON (excluding raw_response which is not serializable)
        json_path = output_path.with_suffix('.json')
        with json_path.open('w', encoding='utf-8') as f:
            json.dump({
                'text': result['text'],
                'model': result['model'],
                'usage': result['usage']
            }, f, indent=2, ensure_ascii=False)

        print(f"  Saved text: {txt_path}")
        print(f"  Saved JSON: {json_path}")

    return result


def ocr_pdf_page(
    pdf_path: Path,
    page_number: int,
    output_dir: Path,
    preprocess: bool = True,
    anthropic_client: Optional[Any] = None
) -> Dict[str, Any]:
    """Extract and OCR a single page from PDF.

    Args:
        pdf_path: Path to PDF file
        page_number: Page to extract (1-indexed)
        output_dir: Directory to save OCR results
        preprocess: Whether to apply image preprocessing
        anthropic_client: Optional injected Anthropic client

    Returns:
        OCR results dictionary
    """
    from pdf2image import convert_from_path
    from preprocess_image import preprocess_for_ocr

    print(f"Processing page {page_number}...")

    # Extract page
    print(f"  Extracting from PDF...")
    images = convert_from_path(
        pdf_path,
        first_page=page_number,
        last_page=page_number,
        dpi=300
    )

    if not images:
        raise ValueError(f"Could not extract page {page_number}")

    image = images[0]

    # Preprocess if requested
    if preprocess:
        print(f"  Preprocessing...")
        image = preprocess_for_ocr(
            image,
            deskew=True,
            contrast=1.3,
            sharpness=1.2,
            denoise=True,
            remove_border=True,
            binarize_mode=None  # Keep grayscale for Claude
        )

    # Run OCR
    print(f"  Running Claude Vision OCR...")

    # Run OCR directly on image object
    result = ocr_image_with_claude(image, anthropic_client)

    # Save results
    output_dir.mkdir(parents=True, exist_ok=True)

    txt_path = output_dir / f"page_{page_number:03d}.txt"
    with txt_path.open('w', encoding='utf-8') as f:
        f.write(result['text'])
    print(f"  Saved text: {txt_path}")

    json_path = output_dir / f"page_{page_number:03d}.json"
    import json
    with json_path.open('w', encoding='utf-8') as f:
        json.dump({
            'text': result['text'],
            'model': result['model'],
            'usage': result['usage']
        }, f, indent=2, ensure_ascii=False)
    print(f"  Saved JSON: {json_path}")

    # Save preprocessed image for reference
    img_path = output_dir / f"page_{page_number:03d}.png"
    image.save(img_path)
    print(f"  Saved image: {img_path}")

    print(f"  ✓ Tokens used: {result['usage']['input_tokens']} in, {result['usage']['output_tokens']} out")

    return result


def main():
    """Test Claude Vision OCR on a sample page."""
    print("="*70)
    print("Claude Vision OCR Test")
    print("="*70)
    print()

    # Load environment variables from .env
    from load_env import load_env, check_api_keys
    load_env()

    # Check for API key
    status = check_api_keys()
    if not status['anthropic']['set']:
        print("Error: Anthropic API key not configured")
        print()
        print("Setup:")
        print("  1. Edit .env file")
        print("  2. Set ANTHROPIC_API_KEY=your-api-key")
        print("  3. See SETUP_API_KEYS.md for details")
        return

    # Test on sample page
    pdf_path = Path(__file__).parent.parent / "source/candidates/DLI_2015_IGNCA_Delhi.pdf"
    if not pdf_path.exists():
        print(f"Error: {pdf_path} not found")
        return

    output_dir = Path(__file__).parent.parent / "ocr_output/claude"

    print("Testing on page 50...")
    print()

    try:
        result = ocr_pdf_page(pdf_path, 50, output_dir, preprocess=True)

        print()
        print("="*70)
        print("Sample Text (first 500 chars):")
        print("="*70)
        print(result['text'][:500])
        print()
        print(f"Model: {result['model']}")
        print(f"Input tokens: {result['usage']['input_tokens']}")
        print(f"Output tokens: {result['usage']['output_tokens']}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
