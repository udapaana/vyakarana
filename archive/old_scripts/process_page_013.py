#!/usr/bin/env python3
"""Process page_013a and page_013b with Google Vision OCR."""

import base64
import requests
import os
from pathlib import Path
from PIL import Image
import io


def ocr_image_file(image_path: Path, api_key: str) -> str:
    """OCR an image file using Google Vision REST API.

    Args:
        image_path: Path to the image file
        api_key: Google Cloud API key

    Returns:
        Extracted text
    """
    print(f"Processing {image_path.name}...")

    # Load and convert image to base64
    with Image.open(image_path) as img:
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()

    # Build request
    url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"

    request_body = {
        "requests": [
            {
                "image": {"content": img_base64},
                "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
                "imageContext": {"languageHints": ["sa", "en"]},
            }
        ]
    }

    # Make request
    print(f"  Calling Google Vision API...")
    response = requests.post(url, json=request_body)

    if response.status_code != 200:
        raise Exception(
            f"Google Vision API error: {response.status_code} - {response.text}"
        )

    result_json = response.json()

    if "responses" not in result_json or not result_json["responses"]:
        raise Exception("No response from Google Vision API")

    vision_response = result_json["responses"][0]

    if "error" in vision_response:
        raise Exception(f"Vision API error: {vision_response['error']}")

    # Extract text
    text = ""
    if "fullTextAnnotation" in vision_response:
        text = vision_response["fullTextAnnotation"]["text"]

    print(f"  ✓ Extracted {len(text)} characters")

    return text


def main():
    """Process the two images."""
    # Load API key from environment
    api_key = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if not api_key:
        print("Error: GOOGLE_APPLICATION_CREDENTIALS not set in environment")
        print("Loading from .env file...")
        env_file = Path(__file__).parent / ".env"
        if env_file.exists():
            with env_file.open() as f:
                for line in f:
                    if line.startswith("GOOGLE_APPLICATION_CREDENTIALS="):
                        api_key = line.split("=", 1)[1].strip().strip('"')
                        break

    if not api_key:
        print("Error: Could not find Google API key")
        return 1

    print("Google Vision OCR - Processing page_013a and page_013b")
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
            text = ocr_image_file(img_path, api_key)

            # Save text
            with txt_path.open("w", encoding="utf-8") as f:
                f.write(text)

            print(f"  ✓ Saved to {txt_path.name}")
            print()

            results.append(
                {"file": txt_name, "path": txt_path, "char_count": len(text)}
            )

        except Exception as e:
            print(f"  ✗ Error: {e}")
            print()
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

    print()
    return 0


if __name__ == "__main__":
    exit(main())
