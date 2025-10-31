#!/usr/bin/env python3
"""
Process OCR pages by calling Claude Code in the current terminal session
This uses your Claude Max subscription instead of API credits
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

class SessionProcessor:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.ocr_claude = self.repo_path / "ocr_output" / "claude"
        self.ocr_google = self.repo_path / "ocr_output" / "google"
        self.output_dir = self.repo_path / "structured_pages"
        self.status_file = self.repo_path / "data" / "processing_status.json"
        self.style_guide_file = self.repo_path / "docs" / "STRUCTURING_RAW_OCR.md"

        self.output_dir.mkdir(exist_ok=True)
        self._load_status()
        self._load_style_guide()

    def _load_status(self):
        if self.status_file.exists():
            self.status = json.loads(self.status_file.read_text())
            if "processed_with_errors" not in self.status:
                self.status["processed_with_errors"] = []
        else:
            self.status = {
                "processed_pages": [],
                "processed_with_errors": [],
                "needs_review": [],
                "validation_failures": [],
                "last_updated": None,
                "total_pages": 0,
                "current_batch": 0
            }

    def _save_status(self):
        self.status["last_updated"] = datetime.now().isoformat()
        self.status_file.write_text(json.dumps(self.status, indent=2))

    def _load_style_guide(self):
        if self.style_guide_file.exists():
            self.style_guide = self.style_guide_file.read_text()
        else:
            print("ERROR: Style guide not found!")
            sys.exit(1)

    def build_prompt_file(self, page_num: int):
        """Build a prompt file for Claude to process"""
        page_name = f"page_{page_num:03d}"

        claude_file = self.ocr_claude / f"{page_name}.txt"
        google_file = self.ocr_google / f"{page_name}.txt"

        if not claude_file.exists() or not google_file.exists():
            print(f"  ❌ OCR files missing for page {page_num}")
            return None

        claude_ocr = claude_file.read_text(encoding='utf-8')
        google_ocr = google_file.read_text(encoding='utf-8')

        # Create prompt file
        prompt_file = self.repo_path / "temp" / f"prompt_page_{page_num}.txt"
        prompt_file.parent.mkdir(exist_ok=True)

        prompt = f"""Process page {page_num} of Kale's Higher Sanskrit Grammar (1894).

You are doing Phase 2: Reconciliation and Structuring of OCR output.

Your task:
1. RECONCILE the two OCR outputs (choose best reading, fix OCR errors)
2. STRUCTURE into markdown with YAML front matter
3. VALIDATE content preservation

STYLE GUIDE EXCERPT (Key Rules):
{self._extract_style_guide_rules()}

CLAUDE OCR:
```
{claude_ocr}
```

GOOGLE OCR:
```
{google_ocr}
```

OUTPUT FORMAT:
Return ONLY a JSON object with this structure:
{{
  "reconciled_text": "raw reconciled text here",
  "structured_markdown": "complete markdown with YAML front matter",
  "validation": {{
    "is_valid": true/false,
    "content_preserved_percentage": 98.5,
    "ocr_corrections_made": 12,
    "differences": []
  }},
  "ocr_corrections": [
    {{"location": "line 23", "original": "ra1an", "corrected": "rājan", "type": "character_misread"}}
  ],
  "metadata": {{
    "topics": ["sandhi", "conjuncts"],
    "terms": [],
    "citations": [],
    "word_index": ["राजन्", "क्ष"]
  }}
}}

Process page {page_num} now and return ONLY the JSON (no markdown wrappers, no explanations).
"""

        prompt_file.write_text(prompt)
        return prompt_file

    def _extract_style_guide_rules(self):
        """Extract key rules from style guide"""
        lines = self.style_guide.split('\n')

        # Get the core rules section
        start_idx = None
        end_idx = None

        for i, line in enumerate(lines):
            if '# Kale\'s Sanskrit Grammar - Structuring Style Guide' in line:
                start_idx = i
            if '# MCP Server Configuration' in line and start_idx:
                end_idx = i
                break

        if start_idx and end_idx:
            rules = '\n'.join(lines[start_idx:end_idx])
            # Limit to first 3000 chars to keep prompt manageable
            return rules[:3000] + "\n\n[... see full style guide for complete rules]"

        return '\n'.join(lines[:200])

    def process_page_interactive(self, page_num: int):
        """Process a page by calling the current Claude Code session"""
        print(f"\n[{page_num}] Processing page {page_num}...")

        # Build prompt file
        prompt_file = self.build_prompt_file(page_num)
        if not prompt_file:
            return False

        print(f"  📝 Prompt saved to: {prompt_file}")
        print(f"  ⚙️  Ready to send to Claude...")
        print(f"\n  🤖 Please run this command in your terminal:")
        print(f"     cat {prompt_file} | claude --print > {self.repo_path}/temp/response_page_{page_num}.json")
        print(f"\n  ⏸️  Press Enter when done...")

        input()

        # Read response
        response_file = self.repo_path / "temp" / f"response_page_{page_num}.json"
        if not response_file.exists():
            print(f"  ❌ Response file not found")
            return False

        response = response_file.read_text()

        # Parse and save
        return self._parse_and_save_response(page_num, response)

    def _parse_and_save_response(self, page_num: int, response: str):
        """Parse Claude's response and save results"""
        page_name = f"page_{page_num:03d}"

        try:
            # Extract JSON
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                print(f"  ❌ No JSON found in response")
                return False

            json_str = response[json_start:json_end]
            data = json.loads(json_str)

            # Save structured markdown
            md_file = self.output_dir / f"{page_name}.md"
            md_file.write_text(data["structured_markdown"], encoding='utf-8')

            # Save validation report
            validation_file = self.output_dir / f"{page_name}_validation.json"
            validation_data = {
                "validation": data["validation"],
                "ocr_corrections": data["ocr_corrections"],
                "timestamp": datetime.now().isoformat()
            }
            validation_file.write_text(
                json.dumps(validation_data, indent=2, ensure_ascii=False)
            )

            # Update status
            if page_name not in self.status["processed_pages"]:
                self.status["processed_pages"].append(page_name)

            self._save_status()

            print(f"  ✅ Saved {page_name}.md")
            print(f"     Content preserved: {data['validation']['content_preserved_percentage']:.1f}%")

            return True

        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Process OCR via Claude Code session')
    parser.add_argument('--page', type=int, required=True, help='Page number to process')

    args = parser.parse_args()

    processor = SessionProcessor('/Users/skmnktl/Downloads/ocr')
    success = processor.process_page_interactive(args.page)

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
