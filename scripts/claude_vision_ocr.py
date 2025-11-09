#!/usr/bin/env python3
"""Claude Vision OCR module for extracting text from PDF pages.

This module provides a reusable interface for OCR using Claude's vision
capabilities, optimized for Sanskrit mixed-script content.

Following coding standards:
- Deep module: Simple interface, complex implementation hidden
- Comments explain why: Why certain prompt engineering choices were made
"""

import base64
import io
import json
import os
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
from PIL import Image
from pdf2image import convert_from_path
import anthropic

# Import preprocessing utilities
from preprocess_image import preprocess_for_ocr


def encode_image_base64(image: Image.Image) -> str:
    """Encode PIL Image to base64 string for Claude API.

    Why JPEG at 95: Balance between quality and API payload size.
    PNG would be lossless but 3-5x larger payloads.
    """
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=95)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def get_claude_client() -> anthropic.Anthropic:
    """Get authenticated Anthropic client.

    Why centralized: Single point for API key management.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        # Try loading from .env
        env_file = Path(__file__).parent.parent / ".env"
        if env_file.exists():
            with env_file.open() as f:
                for line in f:
                    if line.startswith("ANTHROPIC_API_KEY="):
                        api_key = line.split("=", 1)[1].strip()
                        break

    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment or .env file")

    return anthropic.Anthropic(api_key=api_key)


def get_ocr_prompt() -> str:
    """Get the OCR prompt optimized for Sanskrit grammar text.

    Why this prompt: Extensive testing showed character-by-character
    instruction with explicit diacritic list produces best results.
    """
    return """You are doing OCR transcription. Transcribe EVERY SINGLE CHARACTER of text visible in this image exactly as shown.

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


def ocr_image_with_claude(
    image: Image.Image,
    model: str = "claude-3-opus-20240229",
    max_tokens: int = 16000,
) -> Dict:
    """Extract text from image using Claude Vision API.

    Why Sonnet 3.5: Best balance of accuracy and cost for OCR.
    Opus has marginally better accuracy but 3x cost.

    Args:
        image: PIL Image to OCR
        model: Claude model to use
        max_tokens: Maximum output tokens

    Returns:
        Dict with text, usage, and timestamp
    """
    client = get_claude_client()
    image_base64 = encode_image_base64(image)
    prompt = get_ocr_prompt()

    # Call Claude API
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=0,  # Why 0: OCR should be deterministic
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

    return {
        "text": text,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        },
        "model": model,
        "timestamp": datetime.now().isoformat(),
    }


def ocr_pdf_page(
    pdf_path: str,
    page_number: int,
    output_dir: str,
    preprocess: bool = True,
    dpi: int = 300,
    model: str = "claude-3-5-sonnet-20241022",
) -> Dict:
    """Extract text from a PDF page using Claude Vision OCR.

    This is the main entry point for OCR processing. It:
    1. Extracts page from PDF as image
    2. Optionally preprocesses (deskew, denoise, enhance)
    3. Runs Claude Vision OCR
    4. Saves results (txt, json, preprocessed png)

    Args:
        pdf_path: Path to PDF file
        page_number: Page number (1-indexed)
        output_dir: Directory to save outputs
        preprocess: Whether to preprocess image
        dpi: Resolution for PDF extraction
        model: Claude model to use

    Returns:
        Dict with text, usage, timestamp
    """
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Extract page as image
    images = convert_from_path(
        pdf_path, first_page=page_number, last_page=page_number, dpi=dpi
    )

    if not images:
        raise ValueError(f"Could not extract page {page_number} from {pdf_path}")

    image = images[0]

    # Preprocess if requested
    if preprocess:
        image = preprocess_for_ocr(image)

    # Save preprocessed image
    page_base = f"page_{page_number:03d}"
    png_path = output_dir / f"{page_base}.png"
    image.save(png_path, "PNG")

    # Run OCR
    result = ocr_image_with_claude(image, model=model)

    # Save text
    txt_path = output_dir / f"{page_base}.txt"
    txt_path.write_text(result["text"])

    # Save full result JSON
    json_path = output_dir / f"{page_base}.json"
    with json_path.open("w") as f:
        json.dump(result, f, indent=2)

    return result


def main():
    """CLI interface for testing."""
    import argparse

    parser = argparse.ArgumentParser(description="OCR a PDF page with Claude Vision")
    parser.add_argument("pdf", type=Path, help="PDF file path")
    parser.add_argument("page", type=int, help="Page number (1-indexed)")
    parser.add_argument(
        "--output", type=Path, default=Path("ocr_output"), help="Output directory"
    )
    parser.add_argument(
        "--no-preprocess", action="store_true", help="Skip image preprocessing"
    )
    parser.add_argument("--dpi", type=int, default=300, help="DPI for PDF extraction")
    parser.add_argument(
        "--model", default="claude-3-5-sonnet-20241022", help="Claude model to use"
    )

    args = parser.parse_args()

    if not args.pdf.exists():
        print(f"Error: PDF not found: {args.pdf}")
        return 1

    print(f"Processing page {args.page} from {args.pdf.name}")
    print(f"Output: {args.output}")
    print()

    try:
        result = ocr_pdf_page(
            str(args.pdf),
            args.page,
            str(args.output),
            preprocess=not args.no_preprocess,
            dpi=args.dpi,
            model=args.model,
        )

        print(f"✓ Extracted {len(result['text'])} characters")
        print(
            f"✓ Tokens: {result['usage']['input_tokens']} in, "
            f"{result['usage']['output_tokens']} out"
        )
        print(f"✓ Saved to {args.output}/page_{args.page:03d}.{{txt,json,png}}")

        return 0

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
