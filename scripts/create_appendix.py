#!/usr/bin/env python3
"""Create appendix structure for Phase 4"""
from pathlib import Path

APPENDIX_DIR = Path("phase4_appendix")
APPENDIX_DIR.mkdir(exist_ok=True)

# Create main appendix index
appendix_index = """---
title: "Appendix: Prosody"
section: appendix
pages: 535-732
source_pages:
  official_1931: [549-732]
topics: [prosody, versification, metres, Sanskrit-poetry]
---

# Appendix: Prosody

The appendix covers the laws of Sanskrit versification and metrical composition.

## Contents

### Prosody (Prosody)
- Pages 535-586 (external 549-600)
- Covers fundamental rules of Sanskrit verse
- Syllable measurement (mātrā)
- Light and heavy syllables
- Common metres and their patterns

## Structure

Appendix sections are numbered separately from main grammar rules (§1, §2, etc.).

See individual appendix files for detailed content.

## Note

This appendix uses the same internal page numbering system as the main text.
Images are available in `phase4_images/` using internal page numbers (535.png onwards).
"""

(APPENDIX_DIR / "README.md").write_text(appendix_index)

print("=" * 70)
print("APPENDIX STRUCTURE CREATED")
print("=" * 70)
print(f"Created: {APPENDIX_DIR}/")
print(f"  - README.md (appendix index)")
print("\nAppendix covers:")
print("  - Internal pages: 535-732")
print("  - External pages: 549-732")  
print("  - Topic: Prosody (Sanskrit versification)")
print("=" * 70)
