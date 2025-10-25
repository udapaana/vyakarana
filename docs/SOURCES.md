# 7th Edition Sources

## Verified 7th Edition Scans

We have identified multiple digitizations of Kale's **7th Edition (1931)** for quality comparison.

### 1. Official 7th Edition 1931
- **Archive.org ID**: HigherSanskritGrammarKale7thEdition
- **Pages**: 732
- **Size**: 60 MB
- **Notes**: Explicitly labeled "SEVENTH EDITION, Revised and Enlarged" (1931)
- **Path**: `source/candidates/Official_7th_Edition_1931.pdf`
- **Verified**: ✓ Yes (text extraction confirms 7th edition)

### 2. DLI 2015 (IGNCA Delhi)
- **Archive.org ID**: in.ernet.dli.2015.105411
- **Pages**: 729
- **Size**: 20 MB
- **Notes**: Digitized by IGNCA Delhi, image-based scan
- **Path**: `source/candidates/DLI_2015_IGNCA_Delhi.pdf`
- **Verified**: ✓ Likely (page count matches 7th edition closely)

### 3. xMqc 1931 Mulgaokar
- **Archive.org ID**: xMqc_a-higher-sanskrit-grammar-by-moreshwar-ram-chandra-kale-1931-d-v-mulgaokar
- **Status**: ✗ Corrupted PDF (unable to extract pages)
- **Not usable**

## Strategy

Using **same book (7th edition), multiple scans** approach:

1. Compare image quality between verified sources on a page-by-page basis
2. Select the best quality image for each page
3. Run multi-pass OCR (Google Vision + Claude Vision) on best images
4. Intelligently merge OCR results

## Next Steps

1. Implement quality comparison between the 2 verified sources
2. For each page 1-729, select the better quality scan
3. Proceed with multi-pass OCR pipeline
