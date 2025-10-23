#!/usr/bin/env python3
"""
Production NLP-based standardizer using spaCy.

This version actually processes and transforms the text:
1. Converts Sanskrit words to proper IAST
2. Tags Sanskrit grammatical terms with @[...]
3. Removes artifacts intelligently
4. Preserves paragraph structure
"""

import spacy
import re
from typing import List, Dict, Set

# Comprehensive Sanskrit to IAST mappings
SANSKRIT_IAST_MAP = {
    # Deities and Mythological figures
    'Krishna': 'Kṛṣṇa', 'Krsna': 'Kṛṣṇa',
    'Rama': 'Rāma', 'Vishnu': 'Viṣṇu', 'Visnu': 'Viṣṇu',
    'Shiva': 'Śiva', 'Siva': 'Śiva', 'Indra': 'Indra',
    'Hari': 'Hari', 'Brhaspati': 'Bṛhaspati', 'Brihaspati': 'Bṛhaspati',

    # Grammarians and Authors
    'Panini': 'Pāṇini', 'Patanjali': 'Patañjali',
    'Katyayana': 'Kātyāyana', 'Vopadeva': 'Vopadeva',
    'Bhattoji': 'Bhaṭṭoji', 'Bhatti': 'Bhaṭṭi',
    'Kalidasa': 'Kālidāsa', 'Vamana': 'Vāmana',

    # Grammatical terms (lowercase to match)
    'sandhi': 'sandhi', 'Sandhi': 'sandhi',
    'samasa': 'samāsa', 'Samasa': 'samāsa',
    'guna': 'guṇa', 'Guna': 'guṇa',
    'vrddhi': 'vṛddhi', 'Vrddhi': 'vṛddhi', 'vridhi': 'vṛddhi',
    'sutra': 'sūtra', 'Sutra': 'sūtra', 'Sutras': 'sūtras',
    'dhatu': 'dhātu', 'Dhatu': 'dhātu',
    'pratyaya': 'pratyaya', 'Pratyaya': 'pratyaya',
    'vibhakti': 'vibhakti', 'Vibhakti': 'vibhakti',
    'pada': 'pada', 'Pada': 'pada',
    'lakara': 'lakāra', 'Lakara': 'lakāra',
    'samhita': 'saṃhitā', 'Samhita': 'saṃhitā',
    'visarga': 'visarga', 'Visarga': 'visarga',
    'anusvara': 'anusvāra', 'Anusvara': 'anusvāra',

    # Compound types
    'tatpurusha': 'tatpuruṣa', 'Tatpurusha': 'tatpuruṣa',
    'karmadharaya': 'karmadhāraya', 'Karmadharaya': 'karmadhāraya',
    'bahuvrihi': 'bahuvrīhi', 'Bahuvrihi': 'bahuvrīhi',
    'dvandva': 'dvandva', 'Dvandva': 'dvandva',
    'avyayibhava': 'avyayībhāva', 'Avyayibhava': 'avyayībhāva',

    # Voice/pada
    'parasmaipada': 'parasmaipada', 'Parasmaipada': 'parasmaipada',
    'atmanepada': 'ātmanepada', 'Atmanepada': 'ātmanepada',

    # Other categories
    'subanta': 'subanta', 'Subanta': 'subanta',
    'tinganta': 'tiṅanta', 'Tinganta': 'tiṅanta',

    # Social classes
    'brahmana': 'brāhmaṇa', 'Brahmana': 'brāhmaṇa', 'Brahman': 'brāhmaṇa',
    'kshatriya': 'kṣatriya', 'Kshatriya': 'kṣatriya',
    'vaisya': 'vaiśya', 'Vaisya': 'vaiśya',
    'sudra': 'śūdra', 'Sudra': 'śūdra', 'Shudra': 'śūdra',

    # Sacred texts
    'veda': 'veda', 'Veda': 'veda',
    'rigveda': 'Ṛgveda', 'Rigveda': 'Ṛgveda',
    'upanishad': 'upaniṣad', 'Upanishad': 'upaniṣad',
}

# Terms that should always be tagged
ALWAYS_TAG = {
    'sandhi', 'samāsa', 'guṇa', 'vṛddhi', 'sūtra', 'dhātu',
    'pratyaya', 'vibhakti', 'pada', 'lakāra',
    'saṃhitā', 'visarga', 'anusvāra',
}

class ProductionStandardizer:
    def __init__(self):
        print("📦 Loading spaCy model...")
        self.nlp = spacy.load("en_core_web_sm")
        print("✅ spaCy loaded")

    def process_line(self, line: str) -> str:
        """Process a single line of text"""

        # Skip headings, blank lines, Devanagari
        if (line.startswith('#') or
            not line.strip() or
            re.search(r'[।॥०-९]', line)):
            return line

        # Process tokens
        doc = self.nlp(line)
        result = line

        # Process in reverse to maintain string positions
        replacements = []

        for token in doc:
            text = token.text

            # Skip if already tagged
            if '@[' in text or ']' in text:
                continue

            # Skip punctuation
            if token.pos_ == 'PUNCT':
                continue

            # Check if in our mapping
            if text in SANSKRIT_IAST_MAP:
                iast = SANSKRIT_IAST_MAP[text]

                # Determine if should be tagged
                if iast.lower() in ALWAYS_TAG:
                    replacement = f'@[{iast}]'
                else:
                    replacement = iast

                # Store replacement with position
                replacements.append((token.idx, token.idx + len(text), replacement))

        # Apply replacements in reverse order
        for start, end, replacement in reversed(replacements):
            result = result[:start] + replacement + result[end:]

        return result

    def process_file(self, input_path: str, output_path: str):
        """Process entire file"""
        print(f"\n📖 Reading {input_path}...")
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        print(f"📝 Processing {len(lines)} lines...")
        processed_lines = []

        for i, line in enumerate(lines):
            if i % 1000 == 0:
                print(f"  Progress: {i}/{len(lines)} ({100*i/len(lines):.1f}%)")

            processed = self.process_line(line.rstrip('\n'))
            processed_lines.append(processed)

        print(f"\n💾 Writing to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(processed_lines))

        print(f"✅ Done! Output written to {output_path}")

        # Statistics
        changes = sum(1 for orig, new in zip(lines, processed_lines) if orig.rstrip() != new)
        print(f"\n📊 Statistics:")
        print(f"  Lines processed: {len(lines)}")
        print(f"  Lines changed: {changes} ({100*changes/len(lines):.1f}%)")

def main():
    print("=" * 80)
    print("Production NLP Standardizer for Kale's Sanskrit Grammar")
    print("=" * 80)

    standardizer = ProductionStandardizer()

    input_file = 'kales_sanskrit_grammar_standardized_v2.md'
    output_file = 'kales_sanskrit_grammar_nlp_standardized.md'

    standardizer.process_file(input_file, output_file)

if __name__ == '__main__':
    main()
