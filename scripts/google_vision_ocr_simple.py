#!/usr/bin/env python3
"""Simplified Google Vision OCR using REST API with API key.

Since we're using an API key (not service account JSON), we can use
the simpler REST API approach.
"""

import base64
import requests
import io
from pathlib import Path
from typing import Dict, Any
from PIL import Image


def ocr_image_with_google_vision_rest(
    image: Image.Image,
    api_key: str,
    language_hints: list = ['sa', 'en']
) -> Dict[str, Any]:
    """OCR image using Google Vision REST API.

    Args:
        image: PIL Image
        api_key: Google Cloud API key
        language_hints: Language codes

    Returns:
        OCR results dict
    """
    # Convert image to base64
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=95)
    img_base64 = base64.b64encode(buffered.getvalue()).decode()

    # Build request
    url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"

    request_body = {
        "requests": [
            {
                "image": {
                    "content": img_base64
                },
                "features": [
                    {
                        "type": "DOCUMENT_TEXT_DETECTION"
                    }
                ],
                "imageContext": {
                    "languageHints": language_hints
                }
            }
        ]
    }

    # Make request
    response = requests.post(url, json=request_body)

    if response.status_code != 200:
        raise Exception(f"Google Vision API error: {response.status_code} - {response.text}")

    result_json = response.json()

    if 'responses' not in result_json or not result_json['responses']:
        raise Exception("No response from Google Vision API")

    vision_response = result_json['responses'][0]

    if 'error' in vision_response:
        raise Exception(f"Vision API error: {vision_response['error']}")

    # Extract text and structure
    result = {
        'text': '',
        'confidence': 0.0,
        'words': [],
        'blocks': []
    }

    if 'fullTextAnnotation' in vision_response:
        result['text'] = vision_response['fullTextAnnotation']['text']

        # Extract pages/blocks/words
        for page in vision_response['fullTextAnnotation'].get('pages', []):
            for block in page.get('blocks', []):
                block_text = ''
                block_confidences = []

                for paragraph in block.get('paragraphs', []):
                    for word in paragraph.get('words', []):
                        # Build word text from symbols
                        word_text = ''.join([
                            symbol['text']
                            for symbol in word.get('symbols', [])
                        ])

                        # Get confidence
                        word_conf = word.get('confidence', 0.0)
                        block_confidences.append(word_conf)

                        block_text += word_text + ' '

                        result['words'].append({
                            'text': word_text,
                            'confidence': word_conf
                        })

                # Store block
                avg_conf = sum(block_confidences) / len(block_confidences) if block_confidences else 0.0
                result['blocks'].append({
                    'text': block_text.strip(),
                    'confidence': avg_conf
                })

        # Overall confidence
        if result['words']:
            result['confidence'] = sum(w['confidence'] for w in result['words']) / len(result['words'])

    return result


def ocr_pdf_page(
    pdf_path: Path,
    page_number: int,
    output_dir: Path,
    api_key: str,
    preprocess: bool = True
) -> Dict[str, Any]:
    """Extract and OCR a PDF page.

    Args:
        pdf_path: Path to PDF
        page_number: Page to process (1-indexed)
        output_dir: Where to save results
        api_key: Google Cloud API key
        preprocess: Whether to preprocess image

    Returns:
        OCR results
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

    # Preprocess
    if preprocess:
        print(f"  Preprocessing...")
        image = preprocess_for_ocr(
            image,
            deskew=True,
            contrast=1.3,
            sharpness=1.2,
            denoise=True,
            remove_border=True,
            binarize_mode=None
        )

    # Run OCR
    print(f"  Running Google Vision OCR...")
    result = ocr_image_with_google_vision_rest(image, api_key)

    # Save results
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save text
    txt_path = output_dir / f"page_{page_number:03d}.txt"
    with txt_path.open('w', encoding='utf-8') as f:
        f.write(result['text'])
    print(f"  Saved text: {txt_path}")

    # Save image
    img_path = output_dir / f"page_{page_number:03d}.png"
    image.save(img_path)
    print(f"  Saved image: {img_path}")

    print(f"  ✓ Confidence: {result['confidence']:.2%}")

    return result


def main():
    """Test Google Vision REST API."""
    from load_env import load_env, check_api_keys
    import os

    print("="*70)
    print("Google Vision OCR Test (REST API)")
    print("="*70)
    print()

    load_env()
    status = check_api_keys()

    if not status['google']['set']:
        print("Error: Google API key not set in .env")
        return

    api_key = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    print(f"Using API key: {api_key[:10]}...")
    print()

    # Test
    pdf_path = Path(__file__).parent.parent / "source/candidates/DLI_2015_IGNCA_Delhi.pdf"
    if not pdf_path.exists():
        print(f"Error: {pdf_path} not found")
        return

    output_dir = Path(__file__).parent.parent / "ocr_output/google"

    try:
        result = ocr_pdf_page(pdf_path, 50, output_dir, api_key, preprocess=True)

        print()
        print("="*70)
        print("Sample Text (first 500 chars):")
        print("="*70)
        print(result['text'][:500])
        print()
        print(f"Total words: {len(result['words'])}")
        print(f"Confidence: {result['confidence']:.2%}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
