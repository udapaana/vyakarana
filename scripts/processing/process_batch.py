#!/usr/bin/env python3
"""
Batch OCR Processing Script for Kale's Grammar
Uses Claude CLI command for processing without API costs
"""

import json
import os
import subprocess
from pathlib import Path
from datetime import datetime
import sys

class BatchProcessor:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.ocr_claude = self.repo_path / "ocr_output" / "claude"
        self.ocr_google = self.repo_path / "ocr_output" / "google"
        self.output_dir = self.repo_path / "structured_pages"
        self.status_file = self.repo_path / "data" / "processing_status.json"
        self.consistency_file = self.repo_path / "data" / "consistency_data.json"
        self.style_guide_file = self.repo_path / "docs" / "STRUCTURING_RAW_OCR.md"

        # Create output directory
        self.output_dir.mkdir(exist_ok=True)

        # Load or initialize status
        self._load_status()
        self._load_consistency()
        self._load_style_guide()

    def _load_status(self):
        if self.status_file.exists():
            self.status = json.loads(self.status_file.read_text())
            # Add new fields if they don't exist (for backwards compatibility)
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

    def _load_consistency(self):
        if self.consistency_file.exists():
            self.consistency = json.loads(self.consistency_file.read_text())
        else:
            self.consistency = {
                "terms": {},
                "citations": {},
                "abbreviations": {},
                "topics": [],
                "devanagari_words": {}
            }

    def _save_consistency(self):
        self.consistency_file.write_text(
            json.dumps(self.consistency, indent=2, ensure_ascii=False)
        )

    def _load_style_guide(self):
        if self.style_guide_file.exists():
            self.style_guide = self.style_guide_file.read_text()
        else:
            print("ERROR: Style guide not found!")
            sys.exit(1)

    def get_available_pages(self, include_errors=False):
        """Find all pages with both Claude and Google OCR

        Args:
            include_errors: If True, include pages that were processed with errors
        """
        claude_pages = set(int(f.stem.split('_')[1])
                          for f in self.ocr_claude.glob("page_*.txt"))
        google_pages = set(int(f.stem.split('_')[1])
                          for f in self.ocr_google.glob("page_*.txt"))

        both = sorted(claude_pages & google_pages)
        processed = set(int(p.split('_')[1]) for p in self.status["processed_pages"])

        # Handle errors list which may contain dicts or strings
        error_pages = []
        for entry in self.status["processed_with_errors"]:
            if isinstance(entry, dict):
                error_pages.append(int(entry["page"].split('_')[1]))
            else:
                error_pages.append(int(entry.split('_')[1]))

        if include_errors:
            # Include error pages in the remaining list
            remaining = sorted((set(both) - processed) | set(error_pages))
        else:
            remaining = sorted(set(both) - processed)

        return {
            "total": len(both),
            "processed": sorted(processed),
            "errors": sorted(error_pages),
            "remaining": remaining
        }

    def process_page_with_claude(self, page_num: int):
        """Process a single page using Claude CLI"""
        page_name = f"page_{page_num:03d}"

        # Load OCR files
        claude_file = self.ocr_claude / f"{page_name}.txt"
        google_file = self.ocr_google / f"{page_name}.txt"

        if not claude_file.exists() or not google_file.exists():
            print(f"  ❌ OCR files missing for page {page_num}")
            return False

        claude_ocr = claude_file.read_text(encoding='utf-8')
        google_ocr = google_file.read_text(encoding='utf-8')

        # Build prompt
        prompt = self._build_processing_prompt(page_num, claude_ocr, google_ocr)

        # Call Claude CLI
        print(f"  ⚙️  Calling Claude CLI for page {page_num}...")
        try:
            # Remove API key from environment to use Max subscription
            env = os.environ.copy()
            had_key = 'ANTHROPIC_API_KEY' in env
            env.pop('ANTHROPIC_API_KEY', None)
            if had_key:
                print(f"  🔓 Removed API key, using Max subscription")

            result = subprocess.run(
                ['claude', '--print', '--dangerously-skip-permissions'],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                env=env
            )

            if result.returncode != 0:
                print(f"  ❌ Claude CLI error (code {result.returncode})")
                if result.stderr:
                    print(f"     stderr: {result.stderr[:500]}")
                if result.stdout:
                    print(f"     stdout: {result.stdout[:500]}")
                self._mark_as_error(page_name, f"CLI error code {result.returncode}: {result.stderr[:200]}")
                return False

            response = result.stdout

            # Parse response and save
            success = self._parse_and_save_response(page_num, response)
            return success

        except subprocess.TimeoutExpired:
            print(f"  ❌ Timeout processing page {page_num}")
            return False
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False

    def _build_processing_prompt(self, page_num: int, claude_ocr: str, google_ocr: str):
        """Build the complete processing prompt"""

        # Get consistency hints
        topics_hint = ", ".join(self.consistency.get("topics", [])[:20])

        prompt = f"""You are processing page {page_num} of Kale's Higher Sanskrit Grammar (1894).

Your task is to:
1. RECONCILE the two OCR outputs (choose best reading, fix OCR errors)
2. STRUCTURE into markdown with YAML front matter
3. VALIDATE content preservation

STYLE GUIDE (CRITICAL - FOLLOW EXACTLY):
{self._extract_style_guide_section()}

CONSISTENCY HINTS (use these topics/terms):
Topics seen so far: {topics_hint}

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

CRITICAL RULES - SANSKRIT TERM TAGGING (MOST IMPORTANT):
✓ EVERY Sanskrit word MUST be wrapped in @[...] with proper IAST diacritics
✓ This includes: work titles, author names, grammatical terms, technical terms
✓ Examples of what MUST be tagged:
  - Amarakosha → @[amarakośa]
  - Kalidasa → @[kālidāsa]
  - Bhattikavya → @[bhāṭṭikāvya]
  - Sidhantakaumudi → @[siddhāntakaumudī]
  - Atmanepada → @[ātmanepada]
  - Parasmaipad → @[parasmaipada]
  - Bahuvrihi → @[bahuvrīhi]
  - Avyayibhava → @[avyayībhāva]
  - Raghuvamsa → @[raghuvam̐śa]
  - Meghaduta → @[meghadūta]
✓ Tag Sanskrit terms in BOTH front matter YAML AND body content
✓ IAST must be ALL LOWERCASE with proper diacritics (ā ī ū ṛ ṝ ḷ ḹ ṃ ḥ ś ṣ ñ ṇ ṅ ṭ ḍ)
✓ If you see a Romanized Sanskrit word without diacritics, convert to proper IAST
✓ Wrap Devanagari in @deva[...]

FOOTNOTE FORMATTING (CRITICAL):
✓ Convert ALL footnote markers to standard markdown format
✓ In text: use [^1], [^2], [^3] etc. (sequential numbers)
✓ At bottom: use [^1]: content format
✓ Replace symbols: *, †, ‡, §, ×, ¶ → [^1], [^2], [^3], [^4], [^5], [^6]
✓ Example in text: "example here[^1]"
✓ Example at bottom: "[^1]: @deva[ऋत्यकः] @[ṛtyakaḥ] Pāṇ. VII. 1. 127"
✓ Keep all footnote content properly tagged with @deva[...] and @[...]
✓ Number footnotes sequentially in order of appearance

EMPHASIS MARKERS (CRITICAL - STANDARDIZE):
✓ Convert all emphasis markers to @note[type=X]: format
✓ Conversions:
  - "**Obs.**—" → "@note[type=observation]:"
  - "**N. B.**—" → "@note[type=nota-bene]:"
  - "**Exception.**—" → "@note[type=exception]:"
  - "**Note**—" → "@note[type=note]:"
  - "**Remark**—" → "@note[type=remark]:"
✓ Example: "@note[type=nota-bene]: This rule applies universally."
✓ Keep on same line or start of paragraph
✓ Ensure all Sanskrit in notes is tagged with @deva[...] and @[...]

RULE NUMBERS AND HEADERS (CRITICAL):
✓ Rule numbers MUST use markdown headers, NEVER bold
✓ Format: "## § 20. Title of Rule" (space after §, period after number)
✓ For ranges: "## § 31-36. Title" (single §, hyphen between numbers)
✓ NEVER use: **§ 13.** or **§§31** or § 20 without ##
✓ If rule appears mid-paragraph, move to its own heading line
✓ Subsections use standard format: (a), (b), (c) - NOT **(a)**

HEADING HIERARCHY (CRITICAL):
✓ Use proper markdown heading levels:
  - ## for § rule numbers (level 2)
  - ### for major subsections like "Vowels", "Consonants" (level 3)
  - #### for minor subsections if needed (level 4)
✓ NEVER use **Vowels:** - use ### Vowels
✓ NEVER use **§ N.** - always use ## § N.
✓ Section markers (a), (b), (c) are inline text, NOT headings

YAML FORMATTING (CRITICAL):
✓ Always QUOTE all panini_refs entries: ["Pāṇ. VI. 1. 89"]
✓ Never leave panini_refs as empty [] - if no refs, omit the field entirely
✓ Quote all string values in YAML arrays for safety
✓ Ensure YAML is valid and parseable

SANSKRIT IN ALL CONTEXTS (IMPORTANT):
✓ Tag Sanskrit even in headings: "## § 20. Rules of @[guṇa]"
✓ Tag Sanskrit in YAML front matter: full: "@[amarakośa]"
✓ Tag ALL occurrences, not just first mention
✓ Don't skip common abbreviations if they're Sanskrit origin

OTHER RULES:
✓ Fix OCR errors (spacing, character misreads: 0/o, 1/l, rn/m)
✓ Never change author's word choices
✓ Every word from original must appear in output

CRITICAL OUTPUT INSTRUCTION:
Return ONLY the JSON object. No explanations, no markdown code blocks, no commentary.
Start your response with {{ and end with }}.
Do not wrap the JSON in ```json or any other formatting.
Just the raw JSON object and nothing else.

Process page {page_num} now and return ONLY the JSON:"""

        return prompt

    def _extract_style_guide_section(self):
        """Extract key sections from style guide"""
        # For now, return full guide (could optimize later)
        # Extract just the core sections to fit in context
        lines = self.style_guide.split('\n')

        # Find the main style guide section (between the first ## and the MCP section)
        start_idx = None
        end_idx = None

        for i, line in enumerate(lines):
            if '# Kale\'s Sanskrit Grammar - Structuring Style Guide' in line:
                start_idx = i
            if '# MCP Server Configuration' in line and start_idx:
                end_idx = i
                break

        if start_idx and end_idx:
            return '\n'.join(lines[start_idx:end_idx])

        # Fallback: return first 500 lines
        return '\n'.join(lines[:500])

    def _parse_and_save_response(self, page_num: int, response: str):
        """Parse Claude's response and save results"""
        page_name = f"page_{page_num:03d}"

        try:
            # Extract JSON from response (it might have markdown wrapper)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                print(f"  ❌ No JSON found in response")
                print(f"     Response length: {len(response)}")
                print(f"     Response preview: {response[:500]}")
                self._mark_as_error(page_name, "No JSON found in response")
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

            # Remove from errors list if it was previously there (retry success)
            self.status["processed_with_errors"] = [
                e for e in self.status["processed_with_errors"]
                if e["page"] != page_name
            ]

            # Track validation failures
            if not data["validation"].get("is_valid", False):
                if page_name not in self.status["needs_review"]:
                    self.status["needs_review"].append(page_name)

            # Update consistency data
            if "metadata" in data:
                self._update_consistency(page_num, data["metadata"])

            self._save_status()

            print(f"  ✅ Saved {page_name}.md")
            print(f"     Content preserved: {data['validation']['content_preserved_percentage']:.1f}%")
            print(f"     OCR corrections: {data['validation']['ocr_corrections_made']}")

            return True

        except json.JSONDecodeError as e:
            print(f"  ❌ JSON parse error: {e}")
            print(f"     Response preview: {response[:200]}")
            self._mark_as_error(page_name, f"JSON parse error: {e}")
            return False
        except KeyError as e:
            print(f"  ❌ Missing expected field in response: {e}")
            print(f"     Available keys: {list(data.keys()) if 'data' in locals() else 'N/A'}")
            self._mark_as_error(page_name, f"Missing field: {e}")
            return False
        except Exception as e:
            print(f"  ❌ Error saving: {e}")
            import traceback
            traceback.print_exc()
            self._mark_as_error(page_name, f"Error: {e}")
            return False

    def _mark_as_error(self, page_name: str, error_msg: str):
        """Mark a page as processed with errors"""
        if page_name not in self.status["processed_with_errors"]:
            error_entry = {
                "page": page_name,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
            self.status["processed_with_errors"].append(error_entry)
            self._save_status()

    def _update_consistency(self, page_num: int, metadata: dict):
        """Update global consistency tracking"""
        if not metadata:
            return

        # Track topics
        topics = metadata.get("topics", [])
        if topics:
            for topic in topics:
                if topic and topic not in self.consistency["topics"]:
                    self.consistency["topics"].append(topic)

        # Track terms
        terms = metadata.get("terms", [])
        if terms:
            for term in terms:
                if isinstance(term, dict):
                    term_key = term.get("term_iast", "")
                    if term_key and term_key not in self.consistency["terms"]:
                        self.consistency["terms"][term_key] = {
                            "pages": [page_num],
                            "devanagari": term.get("term_deva"),
                            "definition": term.get("definition")
                        }

        # Track Devanagari words
        word_index = metadata.get("word_index", [])
        if word_index:
            for word in word_index:
                if word:
                    if word not in self.consistency["devanagari_words"]:
                        self.consistency["devanagari_words"][word] = []
                    if page_num not in self.consistency["devanagari_words"][word]:
                        self.consistency["devanagari_words"][word].append(page_num)

        self._save_consistency()

    def process_batch(self, batch_size: int = 10, start_page: int = None, reprocess_errors: bool = False):
        """Process a batch of pages

        Args:
            batch_size: Number of pages to process
            start_page: Start from specific page number
            reprocess_errors: If True, reprocess pages that had errors
        """
        pages = self.get_available_pages(include_errors=reprocess_errors)
        remaining = pages["remaining"]

        if not remaining:
            print("✅ All pages processed!")
            return

        # Determine batch
        if start_page is not None:
            batch = [p for p in remaining if p >= start_page][:batch_size]
        else:
            batch = remaining[:batch_size]

        print(f"\n📦 Processing batch of {len(batch)} pages")
        print(f"   Pages: {batch[0]}-{batch[-1]}")
        print(f"   Remaining: {len(remaining)}/{pages['total']}")
        if reprocess_errors:
            print(f"   🔄 Reprocessing errors: {len(pages['errors'])} pages")
        print()

        success_count = 0
        for page_num in batch:
            print(f"[{page_num}/{batch[-1]}] Processing page {page_num}...")
            if self.process_page_with_claude(page_num):
                success_count += 1
            print()

        print(f"\n✅ Batch complete: {success_count}/{len(batch)} successful")
        print(f"📊 Total processed: {len(self.status['processed_pages'])}/{pages['total']}")
        print(f"⚠️  Needs review: {len(self.status['needs_review'])}")
        print(f"❌ Errors: {len(self.status['processed_with_errors'])}")

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Process Kale Grammar OCR in batches')
    parser.add_argument('--batch-size', type=int, default=10, help='Pages per batch')
    parser.add_argument('--start-page', type=int, help='Start from specific page')
    parser.add_argument('--pages', type=str, help='Specific pages to process (comma-separated, e.g. "2,5,10")')
    parser.add_argument('--status', action='store_true', help='Show status only')
    parser.add_argument('--reprocess-errors', action='store_true', help='Reprocess pages that had errors')

    args = parser.parse_args()

    processor = BatchProcessor('/Users/skmnktl/Downloads/ocr')

    if args.status:
        pages = processor.get_available_pages()
        print(f"📊 Processing Status:")
        print(f"   Total pages: {pages['total']}")
        print(f"   Processed: {len(pages['processed'])}")
        print(f"   Remaining: {len(pages['remaining'])}")
        print(f"   Needs review: {len(processor.status['needs_review'])}")
        print(f"   Errors: {len(processor.status['processed_with_errors'])}")
        if processor.status['processed_with_errors']:
            print(f"\n   Pages with errors:")
            for entry in processor.status['processed_with_errors']:
                if isinstance(entry, dict):
                    print(f"      - {entry['page']}: {entry['error']}")
                else:
                    print(f"      - {entry}")
        return

    # Handle specific pages
    if args.pages:
        specific_pages = [int(p.strip()) for p in args.pages.split(',')]
        print(f"\n📦 Processing {len(specific_pages)} specific pages")
        print(f"   Pages: {', '.join(map(str, specific_pages))}")
        print()

        success_count = 0
        for page_num in specific_pages:
            print(f"[{page_num}] Processing page {page_num}...")
            if processor.process_page_with_claude(page_num):
                success_count += 1
            print()

        print(f"\n✅ Complete: {success_count}/{len(specific_pages)} successful")
        return

    processor.process_batch(args.batch_size, args.start_page, args.reprocess_errors)

if __name__ == '__main__':
    main()
