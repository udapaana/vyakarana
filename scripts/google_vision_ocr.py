#!/usr/bin/env python3
"""Google Vision OCR module for Sanskrit text extraction.

Google Vision is excellent for:
- Devanagari script recognition
- Handling complex ligatures
- Robust to image quality variations

Following coding standards:
- Deep module: Simple ocr_image() interface, complex Vision API calls hidden
- Dependency injection: Pass in vision client rather than hardcoding
- Comments explain why: Why Google Vision for Devanagari, why certain settings
"""

import io
from pathlib import Path
from typing import Optional, Dict, Any
from PIL import Image


def ocr_image_with_google_vision(
    image: Image.Image,
    vision_client: Optional[Any] = None,
    language_hints: list[str] = ['sa', 'en'],
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """Extract text from image using Google Cloud Vision API.

    Why Google Vision: Excellent Devanagari recognition, handles complex
    ligatures and conjuncts that are common in Sanskrit.

    Args:
        image: PIL Image object to OCR
        vision_client: Google Vision ImageAnnotatorClient (injected dependency)
        language_hints: Language codes to hint OCR ('sa' = Sanskrit, 'en' = English)

    Returns:
        Dict containing:
            - 'text': Full extracted text
            - 'confidence': Average confidence score (0-1)
            - 'blocks': List of text blocks with positions
            - 'words': List of words with bounding boxes and confidence
    """
    # Lazy import to avoid requiring credentials when module is imported
    try:
        from google.cloud import vision
    except ImportError:
        raise ImportError(
            "google-cloud-vision not installed. "
            "Install with: pip install google-cloud-vision"
        )

    # Create client if not provided (dependency injection pattern)
    if vision_client is None:
        # Use API key if provided, otherwise use default credentials
        if api_key:
            from google.cloud.vision_v1.services.image_annotator import ImageAnnotatorClient
            from google.api_core import client_options as client_options_lib

            # Configure client to use API key
            client_options = client_options_lib.ClientOptions(
                api_key=api_key
            )
            vision_client = ImageAnnotatorClient(client_options=client_options)
        else:
            vision_client = vision.ImageAnnotatorClient()

    # Convert PIL Image to bytes
    # Why JPEG: Smaller upload size, Vision API handles compression artifacts well
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG', quality=95)
    img_byte_arr.seek(0)

    # Create Vision API image object
    vision_image = vision.Image(content=img_byte_arr.read())

    # Configure image context with language hints
    # Why language hints: Helps Vision API choose correct character set and
    # improves accuracy for Sanskrit/Devanagari recognition
    image_context = vision.ImageContext(language_hints=language_hints)

    # Request document text detection
    # Why document_text_detection vs text_detection:
    # - document_text_detection preserves layout, paragraph structure
    # - Better for multi-column text and complex layouts
    # - Returns full page hierarchy (pages > blocks > paragraphs > words)
    response = vision_client.document_text_detection(
        image=vision_image,
        image_context=image_context
    )

    if response.error.message:
        raise Exception(f"Google Vision API error: {response.error.message}")

    # Extract structured results
    result = {
        'text': '',
        'confidence': 0.0,
        'blocks': [],
        'words': [],
        'pages': []
    }

    # Get full text annotation
    if response.full_text_annotation:
        result['text'] = response.full_text_annotation.text

        # Extract pages with structure
        for page in response.full_text_annotation.pages:
            page_data = {
                'width': page.width,
                'height': page.height,
                'blocks': []
            }

            # Extract blocks (paragraphs/sections)
            for block in page.blocks:
                block_text = ''
                block_confidence = 0.0
                word_count = 0

                # Extract paragraphs within block
                for paragraph in block.paragraphs:
                    para_confidence = 0.0
                    para_word_count = 0

                    # Extract words
                    for word in paragraph.words:
                        # Combine symbols to form word
                        word_text = ''.join([
                            symbol.text for symbol in word.symbols
                        ])

                        # Calculate word confidence (average of symbol confidences)
                        word_confidence = sum(
                            symbol.confidence for symbol in word.symbols
                        ) / len(word.symbols) if word.symbols else 0.0

                        block_text += word_text + ' '
                        para_confidence += word_confidence
                        para_word_count += 1

                        # Store word with bounding box
                        vertices = word.bounding_box.vertices
                        result['words'].append({
                            'text': word_text,
                            'confidence': word_confidence,
                            'bbox': [(v.x, v.y) for v in vertices]
                        })

                    if para_word_count > 0:
                        block_confidence += para_confidence
                        word_count += para_word_count

                if word_count > 0:
                    avg_confidence = block_confidence / word_count
                else:
                    avg_confidence = 0.0

                # Store block
                vertices = block.bounding_box.vertices
                page_data['blocks'].append({
                    'text': block_text.strip(),
                    'confidence': avg_confidence,
                    'bbox': [(v.x, v.y) for v in vertices]
                })

                result['blocks'].append({
                    'text': block_text.strip(),
                    'confidence': avg_confidence,
                    'bbox': [(v.x, v.y) for v in vertices]
                })

            result['pages'].append(page_data)

        # Calculate overall confidence
        if result['words']:
            result['confidence'] = sum(
                w['confidence'] for w in result['words']
            ) / len(result['words'])

    return result


def ocr_page_file(
    image_path: Path,
    output_path: Optional[Path] = None,
    vision_client: Optional[Any] = None
) -> Dict[str, Any]:
    """OCR an image file and optionally save results.

    Args:
        image_path: Path to image file
        output_path: Optional path to save OCR results as JSON
        vision_client: Optional injected Vision client

    Returns:
        OCR results dictionary
    """
    import json

    # Load image
    image = Image.open(image_path)

    # Run OCR
    result = ocr_image_with_google_vision(image, vision_client)

    # Save if requested
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save full JSON with structure
        json_path = output_path.with_suffix('.json')
        with json_path.open('w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        # Also save plain text for convenience
        txt_path = output_path.with_suffix('.txt')
        with txt_path.open('w', encoding='utf-8') as f:
            f.write(result['text'])

        print(f"  Saved JSON: {json_path}")
        print(f"  Saved text: {txt_path}")

    return result


def ocr_pdf_page(
    pdf_path: Path,
    page_number: int,
    output_dir: Path,
    preprocess: bool = True,
    vision_client: Optional[Any] = None
) -> Dict[str, Any]:
    """Extract and OCR a single page from PDF.

    Args:
        pdf_path: Path to PDF file
        page_number: Page to extract (1-indexed)
        output_dir: Directory to save OCR results
        preprocess: Whether to apply image preprocessing
        vision_client: Optional injected Vision client

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
        dpi=300  # Why 300 DPI: Good balance of quality and file size for OCR
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
            binarize_mode=None  # Keep grayscale for Google Vision
        )

    # Run OCR
    print(f"  Running Google Vision OCR...")
    output_path = output_dir / f"page_{page_number:03d}"
    result = ocr_page_file(image_path=None, output_path=output_path, vision_client=vision_client)

    # Save preprocessed image for reference
    img_path = output_dir / f"page_{page_number:03d}.png"
    image.save(img_path)
    print(f"  Saved image: {img_path}")

    print(f"  ✓ Confidence: {result['confidence']:.2%}")

    return result


def main():
    """Test Google Vision OCR on a sample page."""
    print("="*70)
    print("Google Vision OCR Test")
    print("="*70)
    print()

    # Load environment variables from .env
    from load_env import load_env, check_api_keys
    load_env()

    # Check for credentials
    status = check_api_keys()
    if not status['google']['set']:
        print("Error: Google Cloud credentials not configured")
        print()
        print("Setup:")
        print("  1. Edit .env file")
        print("  2. Set GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json")
        print("  3. See SETUP_API_KEYS.md for details")
        return

    # Test on sample page
    pdf_path = Path("source/candidates/DLI_2015_IGNCA_Delhi.pdf")
    if not pdf_path.exists():
        print(f"Error: {pdf_path} not found")
        return

    output_dir = Path("ocr_output/google")

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
        print(f"Total words extracted: {len(result['words'])}")
        print(f"Average confidence: {result['confidence']:.2%}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
