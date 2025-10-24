#!/usr/bin/env python3
"""Claude Vision OCR using Claude Code CLI interactively.

Since we're running inside Claude Code, we can use the CLI to process images
by showing them to Claude and asking for transcription.

This script prepares images and creates prompts that you can feed to Claude Code.
"""

from pathlib import Path
from pdf2image import convert_from_path
from preprocess_image import preprocess_for_ocr


def prepare_page_for_claude(
    pdf_path: Path,
    page_number: int,
    output_dir: Path,
    preprocess: bool = True
) -> Path:
    """Extract and preprocess a page, save it for Claude to analyze.

    Args:
        pdf_path: Path to PDF
        page_number: Page to extract (1-indexed)
        output_dir: Where to save the image
        preprocess: Whether to preprocess

    Returns:
        Path to saved image file
    """
    print(f"Preparing page {page_number} for Claude Vision...")

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
            binarize_mode=None
        )

    # Save image
    output_dir.mkdir(parents=True, exist_ok=True)
    img_path = output_dir / f"page_{page_number:03d}.png"
    image.save(img_path)
    print(f"  ✓ Saved: {img_path}")

    return img_path


def create_ocr_prompt(page_number: int) -> str:
    """Create the prompt to give to Claude for OCR.

    Returns:
        Prompt text optimized for Sanskrit grammar OCR
    """
    return f"""Please transcribe all text from page {page_number} of Kale's Higher Sanskrit Grammar.

IMPORTANT INSTRUCTIONS:

1. Preserve ALL text exactly as shown, including:
   - Sanskrit text in Devanagari script (धी, भू, सू, etc.)
   - English text
   - IAST transliteration with diacritical marks (ā, ī, ū, ṛ, ṝ, ḷ, ṃ, ḥ, ṅ, ñ, ṭ, ḍ, ṇ, ś, ṣ)
   - Section markers (§ symbols and numbers)
   - Footnote markers

2. For IAST, be very careful with diacriticals:
   - Long vowels: ā, ī, ū (with macron)
   - Vocalic r: ṛ, ṝ (with dot below)
   - Vocalic l: ḷ, ḹ (with dot below)
   - Nasals: ṃ (anusvāra), ḥ (visarga), ṅ, ñ, ṇ
   - Retroflexes: ṭ, ḍ, ṇ (with dot below)
   - Sibilants: ś (acute accent), ṣ (dot below)

3. Maintain layout:
   - Paragraph breaks
   - Indentation for declension tables
   - Column structure

4. For tables, preserve structure with spacing

5. Mark uncertain text with [?] but provide best reading

Please provide the complete transcription:"""


def main():
    """Prepare pages for manual Claude Vision OCR."""
    print("="*70)
    print("Claude Vision OCR - Manual Mode")
    print("="*70)
    print()
    print("This script prepares images for you to show Claude Code.")
    print("Claude Code (this CLI) will transcribe them interactively.")
    print()

    # Prepare page 50
    pdf_path = Path(__file__).parent.parent / "source/candidates/DLI_2015_IGNCA_Delhi.pdf"
    output_dir = Path(__file__).parent.parent / "ocr_output/claude_manual"

    img_path = prepare_page_for_claude(pdf_path, 50, output_dir, preprocess=True)

    print()
    print("="*70)
    print("Next Steps - Manual OCR with Claude Code")
    print("="*70)
    print()
    print(f"1. The image is ready: {img_path}")
    print()
    print("2. Show it to Claude Code by running:")
    print(f"   Use the Read tool on: {img_path}")
    print()
    print("3. Then provide this prompt:")
    print()
    print("-" * 70)
    print(create_ocr_prompt(50))
    print("-" * 70)
    print()
    print("4. Save Claude's transcription to:")
    print(f"   {output_dir}/page_050.txt")
    print()
    print("This approach uses Claude Code directly without API calls!")


if __name__ == "__main__":
    main()
