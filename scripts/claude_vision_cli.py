#!/usr/bin/env python3
"""Claude Vision OCR using claude CLI command.

Calls the claude CLI programmatically to process images.
"""

import subprocess
from pathlib import Path
from pdf2image import convert_from_path
from preprocess_image import preprocess_for_ocr


def ocr_image_with_claude_cli(image_path: Path) -> str:
    """Run OCR on image using claude CLI.

    Args:
        image_path: Path to image file

    Returns:
        Transcribed text from Claude
    """
    # Craft the prompt for Claude
    prompt = """Please transcribe all text from this page of Kale's Higher Sanskrit Grammar.

IMPORTANT INSTRUCTIONS:

1. Preserve ALL text exactly as shown, including:
   - Sanskrit text in Devanagari script (धी, भू, सू, etc.)
   - English text
   - IAST transliteration with diacritical marks (ā, ī, ū, ṛ, ṝ, ḷ, ṃ, ḥ, ṅ, ñ, ṭ, ḍ, ṇ, ś, ṣ)
   - Section markers (§ symbols and numbers)
   - Footnote markers and numbers

2. For IAST transliteration, be very careful with diacriticals:
   - Long vowels: ā, ī, ū (with macron above)
   - Vocalic r: ṛ, ṝ (with dot below and macron)
   - Vocalic l: ḷ, ḹ (with dot below and macron)
   - Nasals: ṃ (anusvāra - dot above), ḥ (visarga), ṅ, ñ, ṇ
   - Retroflexes: ṭ, ḍ, ṇ (with dot below)
   - Sibilants: ś (acute accent), ṣ (dot below)

3. Maintain layout and structure:
   - Paragraph breaks
   - Indentation for tables/declensions
   - Section numbers and headings

4. For declension tables, preserve the structure with proper spacing

5. Mark any uncertain text with [?] but provide your best reading

Provide ONLY the transcribed text, no explanations or commentary."""

    # Call claude CLI with the image
    # Why this approach: claude CLI can handle images directly
    try:
        result = subprocess.run(
            ['claude', '-p', prompt, str(image_path)],
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )

        if result.returncode != 0:
            raise Exception(f"claude CLI error: {result.stderr}")

        return result.stdout.strip()

    except subprocess.TimeoutExpired:
        raise Exception("claude CLI timeout (>120s)")
    except FileNotFoundError:
        raise Exception("claude CLI not found. Is it installed?")


def ocr_pdf_page(
    pdf_path: Path,
    page_number: int,
    output_dir: Path,
    preprocess: bool = True
) -> dict:
    """Extract and OCR a PDF page using Claude CLI.

    Args:
        pdf_path: Path to PDF
        page_number: Page to process (1-indexed)
        output_dir: Where to save results
        preprocess: Whether to preprocess image

    Returns:
        Dict with 'text' key
    """
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

    # Save image temporarily for claude CLI
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_img_path = output_dir / f"page_{page_number:03d}.png"
    image.save(temp_img_path)
    print(f"  Saved image: {temp_img_path}")

    # Run OCR
    print(f"  Running Claude Vision OCR via CLI...")
    text = ocr_image_with_claude_cli(temp_img_path)

    # Save text
    txt_path = output_dir / f"page_{page_number:03d}.txt"
    with txt_path.open('w', encoding='utf-8') as f:
        f.write(text)
    print(f"  Saved text: {txt_path}")

    print(f"  ✓ Transcribed {len(text)} characters")

    return {'text': text}


def main():
    """Test Claude CLI OCR on a sample page."""
    print("="*70)
    print("Claude Vision OCR Test (CLI)")
    print("="*70)
    print()

    # Test on page 50
    pdf_path = Path(__file__).parent.parent / "source/candidates/DLI_2015_IGNCA_Delhi.pdf"
    output_dir = Path(__file__).parent.parent / "ocr_output/claude"

    if not pdf_path.exists():
        print(f"Error: {pdf_path} not found")
        return

    try:
        result = ocr_pdf_page(pdf_path, 50, output_dir, preprocess=True)

        print()
        print("="*70)
        print("Sample Text (first 500 chars):")
        print("="*70)
        print(result['text'][:500])
        print()
        print(f"Total characters: {len(result['text'])}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
