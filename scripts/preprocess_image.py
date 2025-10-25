#!/usr/bin/env python3
"""Image preprocessing to improve OCR accuracy.

Applies various cleanup operations to scanned pages before OCR:
- Deskewing (straightening rotated pages)
- Contrast enhancement
- Noise reduction
- Binarization (for text clarity)
- Border removal

Following coding standards:
- Deep module: Simple preprocess() interface hides complex image operations
- Comments explain why: Why each operation helps OCR
"""

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from typing import Optional
from pathlib import Path


def deskew_image(image: Image.Image) -> Image.Image:
    """Detect and correct page rotation/skew.

    Why this helps OCR: Skewed text confuses line detection and character
    recognition. Even 1-2 degree rotation can significantly reduce accuracy.

    Uses Hough transform to detect text line angles and rotate to horizontal.
    """
    # Convert to grayscale for angle detection
    gray = image.convert('L')

    # Convert to numpy array
    img_array = np.array(gray)

    # Simple implementation: detect edges, find dominant angle
    # For production, could use more sophisticated skew detection
    try:
        from scipy import ndimage
        from scipy.ndimage import interpolation

        # Threshold to binary
        binary = img_array > 128

        # Calculate angle using projection profile method
        # Why projection: Text lines create peaks in horizontal projection
        def determine_skew(image_array):
            """Determine skew angle using projection profile."""
            angles = np.arange(-5, 5, 0.5)  # Check -5 to +5 degrees
            scores = []

            for angle in angles:
                rotated = interpolation.rotate(image_array, angle, reshape=False, order=0)
                # Project onto vertical axis (sum each row)
                projection = np.sum(rotated, axis=1)
                # Variance of projection indicates how well aligned text is
                score = np.var(projection)
                scores.append(score)

            # Best angle has highest variance (sharpest peaks)
            best_angle = angles[np.argmax(scores)]
            return best_angle

        angle = determine_skew(binary)

        # Only rotate if angle is significant (> 0.5 degrees)
        if abs(angle) > 0.5:
            return image.rotate(angle, resample=Image.BICUBIC, expand=False, fillcolor=255)

    except ImportError:
        # scipy not available, skip deskewing
        pass

    return image


def enhance_contrast(image: Image.Image, factor: float = 1.5) -> Image.Image:
    """Enhance image contrast for better text clarity.

    Why this helps OCR: Low contrast between text and background makes
    character edges fuzzy, reducing recognition accuracy. Enhancing contrast
    makes text stand out more clearly.

    Args:
        image: Input image
        factor: Contrast multiplier (1.0 = no change, >1.0 = more contrast)
    """
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)


def enhance_sharpness(image: Image.Image, factor: float = 1.5) -> Image.Image:
    """Sharpen image to improve text edge definition.

    Why this helps OCR: Blurry scans have poorly defined character edges.
    Sharpening enhances edges, making characters more distinct.
    """
    enhancer = ImageEnhance.Sharpness(image)
    return enhancer.enhance(factor)


def remove_noise(image: Image.Image, filter_size: int = 3) -> Image.Image:
    """Remove salt-and-pepper noise from scanned pages.

    Why this helps OCR: Scanner noise (random black/white pixels) can be
    misinterpreted as diacritical marks or punctuation. Median filter
    removes isolated pixels while preserving text edges.

    Args:
        image: Input image
        filter_size: Size of median filter kernel (odd number)
    """
    # Median filter removes noise while preserving edges
    # Why median: Replaces each pixel with median of neighbors, eliminating outliers
    return image.filter(ImageFilter.MedianFilter(size=filter_size))


def remove_borders(image: Image.Image, threshold: int = 240) -> Image.Image:
    """Remove dark borders or artifacts around page edges.

    Why this helps OCR: Scanner artifacts and book binding shadows at edges
    can confuse page layout detection. Removing them helps OCR focus on content.

    Args:
        image: Input image
        threshold: Brightness threshold for detecting border (0-255)
    """
    # Convert to grayscale for border detection
    gray = image.convert('L')
    img_array = np.array(gray)

    # Find content bounding box (non-white regions)
    # Rows/columns where average brightness < threshold likely have content
    row_means = np.mean(img_array, axis=1)
    col_means = np.mean(img_array, axis=0)

    content_rows = np.where(row_means < threshold)[0]
    content_cols = np.where(col_means < threshold)[0]

    if len(content_rows) == 0 or len(content_cols) == 0:
        # No content detected, return original
        return image

    # Crop to content bounding box with small margin
    margin = 20  # pixels
    top = max(0, content_rows[0] - margin)
    bottom = min(img_array.shape[0], content_rows[-1] + margin)
    left = max(0, content_cols[0] - margin)
    right = min(img_array.shape[1], content_cols[-1] + margin)

    return image.crop((left, top, right, bottom))


def binarize(image: Image.Image, method: str = 'adaptive') -> Image.Image:
    """Convert to black and white for maximum text clarity.

    Why this helps OCR: Pure black text on pure white background is easiest
    for OCR engines. Removes gray-scale ambiguity.

    Args:
        image: Input image
        method: 'simple' (global threshold) or 'adaptive' (local threshold)
    """
    gray = image.convert('L')

    if method == 'simple':
        # Simple global thresholding
        # Why 128: Middle point between black (0) and white (255)
        threshold = 128
        return gray.point(lambda x: 255 if x > threshold else 0, mode='1')

    elif method == 'adaptive':
        # Adaptive thresholding using local neighborhoods
        # Why adaptive: Handles uneven lighting/shadow across page
        img_array = np.array(gray)

        try:
            from scipy import ndimage

            # Local mean in 15x15 window
            local_mean = ndimage.uniform_filter(img_array.astype(float), size=15)
            # Threshold: if pixel > local_mean - offset, it's background (white)
            binary = img_array > (local_mean - 10)

            return Image.fromarray((binary * 255).astype(np.uint8), mode='L')

        except ImportError:
            # Fall back to simple thresholding
            return gray.point(lambda x: 255 if x > 128 else 0, mode='1')

    return gray


def preprocess_for_ocr(
    image: Image.Image,
    deskew: bool = True,
    contrast: float = 1.3,
    sharpness: float = 1.2,
    denoise: bool = True,
    remove_border: bool = True,
    binarize_mode: Optional[str] = None
) -> Image.Image:
    """Complete preprocessing pipeline for OCR optimization.

    Why this order:
    1. Deskew first (affects all other operations)
    2. Remove borders (eliminates noise source)
    3. Denoise (before enhancing)
    4. Enhance contrast and sharpness (amplifies signal)
    5. Binarize last (final cleanup)

    Args:
        image: Input image
        deskew: Whether to straighten rotated pages
        contrast: Contrast enhancement factor (1.0 = no change)
        sharpness: Sharpness enhancement factor (1.0 = no change)
        denoise: Whether to apply noise reduction
        remove_border: Whether to crop borders
        binarize_mode: 'simple', 'adaptive', or None (keep grayscale)

    Returns:
        Preprocessed image optimized for OCR
    """
    result = image.copy()

    # Step 1: Straighten page
    if deskew:
        result = deskew_image(result)

    # Step 2: Remove borders/artifacts
    if remove_border:
        result = remove_borders(result)

    # Step 3: Remove noise
    if denoise:
        result = remove_noise(result)

    # Step 4: Enhance contrast
    if contrast != 1.0:
        result = enhance_contrast(result, contrast)

    # Step 5: Enhance sharpness
    if sharpness != 1.0:
        result = enhance_sharpness(result, sharpness)

    # Step 6: Binarize (optional, some OCR engines prefer grayscale)
    if binarize_mode:
        result = binarize(result, method=binarize_mode)

    return result


def preprocess_page_file(
    input_path: Path,
    output_path: Path,
    **kwargs
) -> None:
    """Preprocess a page image file and save result.

    Args:
        input_path: Path to input image
        output_path: Path to save preprocessed image
        **kwargs: Arguments passed to preprocess_for_ocr()
    """
    image = Image.open(input_path)
    preprocessed = preprocess_for_ocr(image, **kwargs)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    preprocessed.save(output_path)


def main():
    """Example usage and testing."""
    print("="*70)
    print("Image Preprocessing for OCR")
    print("="*70)
    print()
    print("This module provides preprocessing operations:")
    print("  - Deskewing (straightening rotated pages)")
    print("  - Contrast enhancement")
    print("  - Sharpness enhancement")
    print("  - Noise reduction")
    print("  - Border removal")
    print("  - Binarization")
    print()
    print("Use preprocess_for_ocr() in your OCR pipeline:")
    print()
    print("  from preprocess_image import preprocess_for_ocr")
    print("  from PIL import Image")
    print()
    print("  image = Image.open('page.png')")
    print("  clean = preprocess_for_ocr(image)")
    print("  # Now run OCR on 'clean'")
    print()
    print("Why preprocessing helps:")
    print("  - Deskew: Straightens rotated text (even 1-2° hurts OCR)")
    print("  - Contrast: Makes text stand out from background")
    print("  - Sharpness: Improves character edge definition")
    print("  - Denoise: Removes scanner artifacts")
    print("  - Border removal: Eliminates binding shadows")
    print("  - Binarize: Pure B&W is easiest for OCR")


if __name__ == "__main__":
    main()
