#!/usr/bin/env python3
"""Quick test to verify Google API key works."""

import os
from load_env import load_env, check_api_keys

# Load environment
load_env()
status = check_api_keys()

if not status['google']['set']:
    print("Error: Google API key not set in .env")
    exit(1)

# Get API key
api_key = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

print(f"Testing Google Vision API with key: {api_key[:10]}...")
print()

try:
    from google.cloud.vision_v1.services.image_annotator import ImageAnnotatorClient
    from google.api_core import client_options as client_options_lib
    from google.cloud import vision

    # Create client with API key
    client_options = client_options_lib.ClientOptions(api_key=api_key)
    client = ImageAnnotatorClient(client_options=client_options)

    # Create a simple test image (just text)
    from PIL import Image, ImageDraw, ImageFont
    import io

    # Create test image with text
    img = Image.new('RGB', (400, 100), color='white')
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), "Sanskrit Test: संस्कृत", fill='black')

    # Convert to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)

    # Create Vision API image
    vision_image = vision.Image(content=img_byte_arr.read())

    # Test OCR
    # Use the correct method name for the API
    response = client.annotate_image({
        'image': vision_image,
        'features': [{'type_': vision.Feature.Type.DOCUMENT_TEXT_DETECTION}],
    })

    if response.error.message:
        print(f"✗ API Error: {response.error.message}")
        exit(1)

    print("✓ Google Vision API key works!")
    print(f"✓ Detected text: {response.full_text_annotation.text[:100]}")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
