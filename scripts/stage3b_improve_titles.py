#!/usr/bin/env python3
"""
Stage 3B: Improve titles - Create proper descriptive titles for rules 1-50
"""

import re
from pathlib import Path

BASE_DIR = Path("/Users/skmnktl/Downloads/ocr")
STRUCTURED_DIR = BASE_DIR / "phase3_rules/core/structured"

# Manual title mappings based on rule content
TITLE_MAP = {
    1: "Sanskrit Language and Devanāgarī Script",
    2: "The Devanāgarī Alphabet",
    3: "Primary Vowels: Simple and Diphthongs",
    4: "Vowel Accents: Udātta, Anudātta, and Svarita",
    5: "Hard and Soft Consonants",
    6: "Additional Characters: Jihvāmūlīya, Upadhmānīya, and Avagraha",
    7: "Aspiration of Consonants",
    8: "Complete Classification of Letters",
    9: "Homogeneous Letters (Savarṇa)",
    10: "Definition of Vowels (Svara)",
    11: "Definition of Syllable (Akṣara)",
    12: "Vowel Sign Forms",
    13: "Importance of Sandhi in Sanskrit",
    14: "Short Vowels Before Conjunct Consonants",
    15: "Prosodial Length of Vowels and Syllables",
    16: "Semivowels as Optional Substitutes",
    17: "Sanskrit Numerical Figures",
    18: "Definition of Sandhi",
    19: "Similar Vowel Coalescence",
    20: "Guṇa Substitution",
    21: "Vṛddhi Substitution",
    22: "Semivowel Substitution Before Dissimilar Vowels",
    23: "Optional Retention of Final इ, उ, ऋ, लृ",
    24: "Diphthongs Before Vowels",
    25: "Pragṛhya Vowels",
    26: "Cases Where Sandhi is Prohibited",
    27: "Particle उ After Consonants",
    28: "Dental and Sibilant Conversions",
    29: "स् Before क्",
    30: "Final Consonants Before Vowels",
    31: "Dental Before ल्",
    32: "स्था and स्तम्भ After Prefixes",
    33: "स् After First Four Letters of a Class",
    34: "Consonants Before Soft Letters",
    35: "श After Hard Consonants",
    36: "Final म् Converted to Anusvāra",
    37: "Anusvāra Before Consonants",
    38: "ह् and ण् Before Sibilants",
    39: "Final Sibilants Before त्, ट्",
    40: "Final त् Before श्",
    41: "Cerebral ण् After इ, ई, उ, ऊ, ऋ, ॠ",
    42: "षु in Substitutes and Terminations",
    43: "षु After Anusvāra and Visarga",
    44: "च् Inserted Between छ् and Vowel",
    45: "Final स् and र् Converted to Visarga",
    46: "Visarga Before च्, छ्, ट्, ठ्, त्, थ्",
    47: "Visarga After Short अ",
    48: "Visarga After आ",
    49: "Visarga After Other Vowels",
    50: "Final स् of Pronouns तत् and एतत्",
}


def improve_title(rule_num: int, file_path: Path) -> bool:
    """Improve the title in a structured rule file"""

    if rule_num not in TITLE_MAP:
        print(f"  Warning: No title mapping for rule {rule_num}")
        return False

    new_title = TITLE_MAP[rule_num]

    try:
        content = file_path.read_text(encoding="utf-8")

        # Replace the title in YAML frontmatter
        content = re.sub(
            r'^title: ".+"$',
            f'title: "{new_title}"',
            content,
            count=1,
            flags=re.MULTILINE,
        )

        # Replace the title in the markdown heading
        # Find the first ## heading after the frontmatter
        parts = content.split("---", 2)
        if len(parts) >= 3:
            yaml_front = parts[1]
            body = parts[2]

            # Replace first ## heading
            body = re.sub(
                r"^## .+$", f"## {new_title}", body, count=1, flags=re.MULTILINE
            )

            content = f"---{yaml_front}---{body}"

        file_path.write_text(content, encoding="utf-8")
        return True

    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    """Improve titles for all rules 1-50"""
    print("Stage 3B: Improving Titles for Rules 1-50")
    print("=" * 60)

    successful = 0
    failed = 0

    for rule_num in range(1, 51):
        file_path = STRUCTURED_DIR / f"rule_{rule_num:03d}.md"

        if not file_path.exists():
            print(f"Rule {rule_num:03d}: File not found")
            failed += 1
            continue

        print(f"Rule {rule_num:03d}: ", end="")

        if improve_title(rule_num, file_path):
            print(f"✓ {TITLE_MAP.get(rule_num, 'Unknown')}")
            successful += 1
        else:
            failed += 1

    print("\n" + "=" * 60)
    print(f"SUMMARY:")
    print(f"  Total processed: {successful + failed}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit(main())
