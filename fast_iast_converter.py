#!/usr/bin/env python3
"""
Fast IAST converter using regex and dictionary mappings (no NLP overhead).

Much faster than spaCy for our use case since we have a known dictionary.
"""

import re
from typing import Dict

# Complete IAST mapping dictionary
IAST_MAP = {
    # Deities
    'Krishna': 'Kṛṣṇa', 'Krsna': 'Kṛṣṇa',
    'Rama': 'Rāma', 'Vishnu': 'Viṣṇu', 'Visnu': 'Viṣṇu',
    'Shiva': 'Śiva', 'Siva': 'Śiva', 'Indra': 'Indra',
    'Hari': 'Hari', 'Brhaspati': 'Bṛhaspati', 'Brihaspati': 'Bṛhaspati',

    # Grammarians
    'Panini': 'Pāṇini', 'Patanjali': 'Patañjali',
    'Katyayana': 'Kātyāyana', 'Vopadeva': 'Vopadeva',
    'Bhattoji': 'Bhaṭṭoji', 'Bhatti': 'Bhaṭṭi',
    'Kalidasa': 'Kālidāsa', 'Vamana': 'Vāmana',
    'Bhartrhari': 'Bhartṛhari',

    # Grammatical terms
    'Sandhi': 'sandhi', 'sandhi': 'sandhi',
    'Samasa': 'samāsa', 'samasa': 'samāsa',
    'Guna': 'guṇa', 'guna': 'guṇa',
    'Vrddhi': 'vṛddhi', 'vrddhi': 'vṛddhi', 'Vridhi': 'vṛddhi', 'vridhi': 'vṛddhi',
    'Sutra': 'sūtra', 'sutra': 'sūtra', 'Sutras': 'sūtras', 'sutras': 'sūtras',
    'Dhatu': 'dhātu', 'dhatu': 'dhātu',
    'Pratyaya': 'pratyaya', 'pratyaya': 'pratyaya',
    'Vibhakti': 'vibhakti', 'vibhakti': 'vibhakti',
    'Pada': 'pada', 'pada': 'pada',
    'Lakara': 'lakāra', 'lakara': 'lakāra',
    'Samhita': 'saṃhitā', 'samhita': 'saṃhitā',
    'Visarga': 'visarga', 'visarga': 'visarga',
    'Anusvara': 'anusvāra', 'anusvara': 'anusvāra',
    'Prakriya': 'prakriyā', 'prakriya': 'prakriyā',

    # Compound types
    'Tatpurusha': 'tatpuruṣa', 'tatpurusha': 'tatpuruṣa',
    'Karmadharaya': 'karmadhāraya', 'karmadharaya': 'karmadhāraya',
    'Bahuvrihi': 'bahuvrīhi', 'bahuvrihi': 'bahuvrīhi',
    'Dvandva': 'dvandva', 'dvandva': 'dvandva',
    'Avyayibhava': 'avyayībhāva', 'avyayibhava': 'avyayībhāva',
    'Upapada': 'upapada', 'upapada': 'upapada',

    # Voice
    'Parasmaipada': 'parasmaipada', 'parasmaipada': 'parasmaipada',
    'Atmanepada': 'ātmanepada', 'atmanepada': 'ātmanepada',

    # Categories
    'Subanta': 'subanta', 'subanta': 'subanta',
    'Tinganta': 'tiṅanta', 'tinganta': 'tiṅanta',
    'Krit': 'kṛt', 'krit': 'kṛt',
    'Taddhita': 'taddhita', 'taddhita': 'taddhita',

    # Social classes
    'Brahmana': 'brāhmaṇa', 'brahmana': 'brāhmaṇa', 'Brahman': 'brāhmaṇa',
    'Kshatriya': 'kṣatriya', 'kshatriya': 'kṣatriya',
    'Vaisya': 'vaiśya', 'vaisya': 'vaiśya',
    'Sudra': 'śūdra', 'sudra': 'śūdra', 'Shudra': 'śūdra', 'shudra': 'śūdra',

    # Texts/Works
    'Veda': 'veda', 'veda': 'veda',
    'Rigveda': 'Ṛgveda', 'rigveda': 'Ṛgveda',
    'Upanishad': 'upaniṣad', 'upanishad': 'upaniṣad',
    'Mahabharata': 'Mahābhārata', 'mahabharata': 'mahābhārata',
    'Ramayana': 'Rāmāyaṇa', 'ramayana': 'rāmāyaṇa',
}

# Terms to always tag
TAG_TERMS = {
    'sandhi', 'samāsa', 'guṇa', 'vṛddhi', 'sūtra', 'dhātu',
    'pratyaya', 'vibhakti', 'pada', 'lakāra', 'saṃhitā',
}

def convert_to_iast(text: str) -> str:
    """Convert Sanskrit words to IAST and tag grammatical terms"""

    # Build pattern for all dictionary words (word boundaries)
    pattern = r'\b(' + '|'.join(re.escape(k) for k in IAST_MAP.keys()) + r')\b'

    def replace_func(match):
        word = match.group(1)
        iast = IAST_MAP[word]

        # Tag if it's a grammatical term
        if iast.lower() in TAG_TERMS:
            # Check if not already tagged
            start = match.start()
            if start > 1 and text[start-2:start] == '@[':
                return iast  # Already tagged
            return f'@[{iast}]'
        return iast

    return re.sub(pattern, replace_func, text)

def process_file(input_path: str, output_path: str):
    """Process entire file quickly"""
    print(f"📖 Reading {input_path}...")
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"📝 Processing {len(lines)} lines...")
    processed = []
    changes = 0

    for i, line in enumerate(lines):
        if i % 2000 == 0 and i > 0:
            print(f"  Progress: {i}/{len(lines)} ({100*i/len(lines):.1f}%) - {changes} changes so far")

        # Skip headings, blank lines, and Devanagari
        if line.startswith('#') or not line.strip() or re.search(r'[।॥०-९]', line):
            processed.append(line)
            continue

        new_line = convert_to_iast(line)
        if new_line != line:
            changes += 1
        processed.append(new_line)

    print(f"\n💾 Writing to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(processed)

    print(f"\n✅ Complete!")
    print(f"📊 Statistics:")
    print(f"  Lines processed: {len(lines)}")
    print(f"  Lines with changes: {changes} ({100*changes/len(lines):.1f}%)")

if __name__ == '__main__':
    print("=" * 80)
    print("Fast IAST Converter for Kale's Sanskrit Grammar")
    print("=" * 80)
    print()

    process_file(
        'kales_sanskrit_grammar_standardized_v2.md',
        'kales_sanskrit_grammar_iast.md'
    )
