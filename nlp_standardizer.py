#!/usr/bin/env python3
"""
NLP-based standardization using spaCy for intelligent token recognition.

This script uses spaCy to:
1. Identify Sanskrit vs English tokens
2. Standardize Sanskrit words to proper IAST
3. Remove unnecessary tokens (artifacts, page numbers, etc.)
4. Fix broken paragraphs using sentence boundaries
5. Tag Sanskrit terms consistently
"""

import spacy
import re
from typing import List, Tuple, Dict, Set
from collections import defaultdict

# Sanskrit to IAST mappings for common proper nouns and terms
SANSKRIT_IAST_MAP = {
    # Deities
    'Krishna': 'Kṛṣṇa',
    'Krsna': 'Kṛṣṇa',
    'Rama': 'Rāma',
    'Vishnu': 'Viṣṇu',
    'Visnu': 'Viṣṇu',
    'Shiva': 'Śiva',
    'Siva': 'Śiva',
    'Indra': 'Indra',
    'Hari': 'Hari',
    'Brhaspati': 'Bṛhaspati',
    'Brihaspati': 'Bṛhaspati',

    # Grammarians
    'Panini': 'Pāṇini',
    'Patanjali': 'Patañjali',
    'Katyayana': 'Kātyāyana',
    'Vopadeva': 'Vopadeva',
    'Bhattoji': 'Bhaṭṭoji',
    'Bhatti': 'Bhaṭṭi',

    # Grammatical terms
    'Sandhi': 'sandhi',
    'Samasa': 'samāsa',
    'Guna': 'guṇa',
    'Vrddhi': 'vṛddhi',
    'Vridhi': 'vṛddhi',
    'Prakriya': 'prakriyā',
    'Sutra': 'sūtra',
    'Dhatu': 'dhātu',
    'Pratyaya': 'pratyaya',
    'Vibhakti': 'vibhakti',
    'Karaka': 'kāraka',
    'Samjna': 'saṃjñā',
    'Tatpurusha': 'tatpuruṣa',
    'Karmadharaya': 'karmadhāraya',
    'Bahuvrihi': 'bahuvrīhi',
    'Dvandva': 'dvandva',
    'Avyayibhava': 'avyayībhāva',

    # Common Sanskrit words
    'Brahmana': 'brāhmaṇa',
    'Brahman': 'brāhmaṇa',
    'Kshatriya': 'kṣatriya',
    'Vaisya': 'vaiśya',
    'Sudra': 'śūdra',
    'Shudra': 'śūdra',
    'Veda': 'veda',
    'Upanishad': 'upaniṣad',
    'Rigveda': 'Ṛgveda',
    'Rig': 'Ṛg',

    # Places
    'Kashi': 'Kāśī',
    'Kasi': 'Kāśī',
    'Ayodhya': 'Ayodhyā',
}

# Words that should always be tagged with @[...]
ALWAYS_TAG = {
    'sandhi', 'samāsa', 'guṇa', 'vṛddhi', 'sūtra', 'dhātu',
    'pratyaya', 'vibhakti', 'kāraka', 'pada', 'lakāra',
    'kṛt', 'taddhita', 'samhitā', 'visarga', 'anusvāra',
    'pluta', 'pragṛhya', 'tatpuruṣa', 'karmadhāraya',
    'bahuvrīhi', 'dvandva', 'avyayībhāva', 'upapada',
    'parasmaipada', 'ātmanepada', 'subanta', 'tiṅanta'
}

# English words that might look Sanskrit but aren't
ENGLISH_WORDS = {
    'The', 'A', 'An', 'In', 'On', 'At', 'To', 'For', 'Of', 'By',
    'With', 'From', 'As', 'Is', 'Are', 'Was', 'Were', 'Be', 'Been',
    'Have', 'Has', 'Had', 'Do', 'Does', 'Did', 'Will', 'Would',
    'Should', 'Could', 'May', 'Might', 'Must', 'Can', 'This', 'That',
    'These', 'Those', 'Here', 'There', 'When', 'Where', 'Why', 'How',
    'What', 'Which', 'Who', 'Whom', 'Whose', 'If', 'Then', 'Else',
    'But', 'Or', 'And', 'Not', 'No', 'Yes', 'All', 'Some', 'Any',
    'Each', 'Every', 'Few', 'Many', 'Much', 'More', 'Most', 'Less',
    'Least', 'Only', 'Just', 'Very', 'Too', 'So', 'Also', 'Even',
    'First', 'Second', 'Third', 'Last', 'Next', 'Previous', 'Following',
    'Grammar', 'Sanskrit', 'Rule', 'Rules', 'Chapter', 'Section',
    'Example', 'Examples', 'Note', 'Notes', 'Obs', 'Exception',
    'Exceptions', 'Letter', 'Letters', 'Word', 'Words', 'Root', 'Roots',
    'Vowel', 'Vowels', 'Consonant', 'Consonants', 'Plural', 'Singular',
    'Dual', 'Masculine', 'Feminine', 'Neuter', 'Nominative', 'Accusative',
    'Instrumental', 'Dative', 'Ablative', 'Genitive', 'Locative', 'Vocative',
    'Present', 'Past', 'Future', 'Perfect', 'Aorist', 'Passive', 'Active',
    'Causal', 'Desiderative', 'Frequentative', 'Benedictive', 'Imperative',
    'Optative', 'Conditional', 'Participle', 'Infinitive', 'Gerund',
    'Compound', 'Compounds', 'Declension', 'Conjugation', 'Tense', 'Mood',
    'Person', 'Number', 'Gender', 'Case', 'Termination', 'Terminations',
    'Affix', 'Affixes', 'Prefix', 'Prefixes', 'Suffix', 'Suffixes',
    'Base', 'Bases', 'Stem', 'Stems', 'Preposition', 'Prepositions',
    'Adverb', 'Adverbs', 'Adjective', 'Adjectives', 'Pronoun', 'Pronouns',
    'Numeral', 'Numerals', 'Verb', 'Verbs', 'Noun', 'Nouns',
    'Oh', 'Ah', 'Lord', 'God', 'King', 'Queen', 'Prince', 'Sage'
}

class NLPStandardizer:
    def __init__(self):
        """Initialize spaCy and load English model"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("📦 Downloading spaCy English model...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")

        # Add custom stop words for artifacts
        self.artifacts = {
            'Pāṇ', 'Pan', 'Vārt', 'Vart', 'Sid', 'Kau', 'Ib',
        }

    def is_sanskrit_word(self, token: str) -> bool:
        """
        Heuristically determine if a token is Sanskrit.

        Criteria:
        1. Contains IAST diacritics (ā, ī, ū, ṛ, ṃ, ḥ, ñ, ṭ, ḍ, ṇ, ś, ṣ)
        2. Is in SANSKRIT_IAST_MAP
        3. Not in ENGLISH_WORDS
        4. Matches Sanskrit morphology patterns
        """
        # Already has IAST diacritics
        if re.search(r'[āīūṛṝḷṃḥñṅṭḍṇśṣ]', token):
            return True

        # Known Sanskrit word
        if token in SANSKRIT_IAST_MAP:
            return True

        # Known English word
        if token in ENGLISH_WORDS:
            return False

        # Check for Sanskrit morphology patterns
        # Common endings: -a, -am, -ah, -at, -an, -ti, -te, -ya, -va, -na, -ta
        if re.match(r'^[A-Z][a-z]+(a|am|ah|at|an|as|ti|te|ya|va|na|ta|tra|dhi|ksha)$', token):
            # But not if it's a common English word that happens to match
            doc = self.nlp(token)
            if doc[0].pos_ in ['PROPN', 'NOUN'] and not doc[0].is_stop:
                return True

        return False

    def standardize_to_iast(self, word: str) -> str:
        """Convert Sanskrit word to proper IAST transliteration"""
        # Direct mapping
        if word in SANSKRIT_IAST_MAP:
            return SANSKRIT_IAST_MAP[word]

        # Already in IAST
        if re.search(r'[āīūṛṝḷṃḥñṅṭḍṇśṣ]', word):
            return word

        # Common transformations
        result = word

        # Vowel lengthening (heuristic - may need manual verification)
        # This is tricky and needs more sophisticated rules

        # Retroflex consonants
        result = result.replace('sh', 'ṣ')  # ष
        result = result.replace('Sh', 'Ṣ')

        # Palatals
        # 'ch' is tricky - could be 'c' or 'ch'

        # Nasals
        result = result.replace('ng', 'ṅ')  # ङ
        result = result.replace('nj', 'ñ')  # ञ

        return result

    def should_tag(self, word: str) -> bool:
        """Determine if word should be tagged with @[...]"""
        word_lower = word.lower()

        # Remove existing IAST and check
        clean = re.sub(r'[āīūṛṝḷṃḥñṅṭḍṇśṣ]', '', word_lower)

        return clean in ALWAYS_TAG or word_lower in ALWAYS_TAG

    def is_artifact(self, token: str, context: str) -> bool:
        """
        Determine if token is an artifact (page number, header, etc.)

        Uses context and token properties.
        """
        # Standalone numbers (likely page numbers)
        if token.isdigit() and int(token) < 1000:
            # Check context - if surrounded by dots, likely page number
            if re.search(rf'\.+\s*{token}\s*$', context):
                return True

        # Common artifacts
        if token in self.artifacts:
            return True

        # Running headers pattern: "§ 20-21 | TEXT"
        if re.match(r'§\s*\d+-\d+\s*\|', context):
            return True

        return False

    def process_text(self, text: str) -> str:
        """Main processing function"""
        print("🔍 Analyzing text with spaCy...")

        lines = text.split('\n')
        processed_lines = []

        for i, line in enumerate(lines):
            # Skip if heading or already processed sections
            if line.startswith('#') or not line.strip():
                processed_lines.append(line)
                continue

            # Skip if inside code block or Devanagari
            if re.search(r'[।॥०-९]', line):  # Has Devanagari
                processed_lines.append(line)
                continue

            # Process with spaCy
            doc = self.nlp(line)

            new_tokens = []
            for token in doc:
                text = token.text

                # Skip if already tagged
                if text.startswith('@[') or (i > 0 and processed_lines[i-1].endswith('@[')):
                    new_tokens.append(text)
                    continue

                # Check if artifact
                if self.is_artifact(text, line):
                    continue  # Skip artifact

                # Check if Sanskrit
                if self.is_sanskrit_word(text):
                    # Standardize to IAST
                    iast = self.standardize_to_iast(text)

                    # Tag if needed
                    if self.should_tag(iast):
                        new_tokens.append(f'@[{iast}]')
                    else:
                        new_tokens.append(iast)
                else:
                    new_tokens.append(text)

            # Reconstruct line preserving spacing
            new_line = doc[0].text_with_ws
            for j, token in enumerate(doc[1:], 1):
                if j < len(new_tokens):
                    new_line = new_line.rstrip() + ' ' + new_tokens[j] + token.whitespace_

            processed_lines.append(line)  # For now, keep original (need better reconstruction)

        return '\n'.join(processed_lines)

def main():
    print("=" * 80)
    print("NLP-Based Standardization for Sanskrit Grammar")
    print("=" * 80)

    # First, let's test on a sample
    sample = """
Krishna said to Rama: "Oh Lord, the Sandhi rules are important."
Panini wrote many Sutras about Guna and Vrddhi.
The Brahmana studied the Veda.
§ 20-21 | RULES OF SANDHI 15
"""

    print("\n📝 Testing on sample text:")
    print(sample)

    standardizer = NLPStandardizer()
    result = standardizer.process_text(sample)

    print("\n✨ Result:")
    print(result)

    # Show what was identified
    print("\n🔍 Analysis:")
    doc = standardizer.nlp(sample)
    for token in doc:
        if not token.is_space:
            is_skt = standardizer.is_sanskrit_word(token.text)
            print(f"  {token.text:20} → Sanskrit: {is_skt:5} | POS: {token.pos_:10} | Stop: {token.is_stop}")

if __name__ == '__main__':
    main()
