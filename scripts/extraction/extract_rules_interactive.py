#!/usr/bin/env python3
"""
Interactive rule extraction that outputs prompts for Claude Code to process.

This script generates extraction tasks that can be fed to Claude Code directly,
avoiding external API calls.
"""

import yaml
from pathlib import Path
import json


class InteractiveRuleExtractor:
    def __init__(self, structured_pages_dir: Path, output_dir: Path):
        self.structured_pages_dir = structured_pages_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Get sorted list of all pages
        self.all_pages = sorted(
            self.structured_pages_dir.glob('page_*.md'),
            key=lambda p: int(p.stem.split('_')[1])
        )
        print(f"Found {len(self.all_pages)} structured pages")

    def read_pages(self, start_page: int, num_pages: int = 5) -> tuple[str, list[int]]:
        """Read multiple pages starting from start_page."""
        pages_content = []
        page_numbers = []

        for page_file in self.all_pages:
            page_num = int(page_file.stem.split('_')[1])
            if page_num < start_page:
                continue
            if page_num >= start_page + num_pages:
                break

            content = page_file.read_text()
            pages_content.append(f"=== PAGE {page_num} ===\n{content}\n")
            page_numbers.append(page_num)

        return '\n'.join(pages_content), page_numbers

    def generate_extraction_task(self, rule_num: int, start_page: int, max_pages: int = 10):
        """Generate the content for Claude to process."""
        pages_content, page_numbers = self.read_pages(start_page, max_pages)

        return {
            'rule_num': rule_num,
            'start_page': start_page,
            'page_numbers': page_numbers,
            'pages_content': pages_content
        }

    def save_extraction_result(self, rule_num: int, content: str, source_pages: list[int]):
        """Save extracted rule content to file."""
        rule_file = self.output_dir / f"rule_{rule_num}.md"

        yaml_data = {
            'rule': f'§ {rule_num}',
            'source_pages': source_pages
        }

        with open(rule_file, 'w', encoding='utf-8') as f:
            f.write('---\n')
            f.write(yaml.dump(yaml_data, allow_unicode=True, sort_keys=False))
            f.write('---\n\n')
            f.write(content)

        return rule_file


def main():
    """Generate the first extraction task."""
    base_dir = Path('/Users/skmnktl/Downloads/ocr')
    structured_pages_dir = base_dir / 'structured_pages'
    output_dir = base_dir / 'rules_llm'

    extractor = InteractiveRuleExtractor(structured_pages_dir, output_dir)

    # Generate task for rule 1
    task = extractor.generate_extraction_task(rule_num=1, start_page=1, max_pages=10)

    print(f"\n=== EXTRACTION TASK FOR RULE {task['rule_num']} ===")
    print(f"Pages to analyze: {task['page_numbers']}\n")
    print(task['pages_content'])

    return extractor, task


if __name__ == '__main__':
    extractor, task = main()
