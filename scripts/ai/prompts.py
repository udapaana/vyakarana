"""
Prompt templates for rule extraction
"""

from typing import Dict, List, Optional


class PromptTemplates:
    """
    Pre-defined prompts for Phase 3 rule extraction
    """

    # System prompt for rule extraction
    SYSTEM_RULE_EXTRACTION = """You are an expert at extracting Sanskrit grammar rules from OCR'd text.

Your task is to extract individual rules (§ N) from structured markdown pages and format them correctly.

Key requirements:
1. Extract ONLY the specified rule number (e.g., § 77)
2. Include the rule title, explanation, examples, and all related content
3. Preserve YAML front matter with proper metadata
4. Maintain Devanagari script (@deva[...]) and IAST transliteration (@[...]) tags
5. Keep footnotes and cross-references intact
6. Stop when you reach the next rule or section boundary
7. Return the end page number where the rule ends

Output format:
- First line: JSON with {"end_page": N}
- Followed by: Complete markdown content for the rule"""

    # System prompt for appendix extraction
    SYSTEM_APPENDIX_EXTRACTION = """You are an expert at extracting Sanskrit grammar appendices from OCR'd text.

Your task is to extract appendix sections (Prosody, Dhātukośa) and format them as searchable tables.

Key requirements:
1. Extract complete appendix section with all entries
2. Convert to markdown table format where applicable
3. Preserve Sanskrit terms in both Devanagari and IAST
4. Include definitions, classifications, and examples
5. Maintain cross-references to main rules

Output format: Structured markdown with tables and proper formatting"""

    @staticmethod
    def extract_rule(
        rule_number: int,
        pages_content: List[str],
        start_page: int,
    ) -> str:
        """
        Generate prompt for extracting a specific rule

        Args:
            rule_number: Rule number to extract (1-972)
            pages_content: List of page contents to search
            start_page: Starting page number

        Returns:
            Formatted prompt string
        """
        pages_text = "\n\n---PAGE_BREAK---\n\n".join(
            f"=== PAGE {start_page + i} ===\n{content}"
            for i, content in enumerate(pages_content)
        )

        return f"""Extract rule § {rule_number} from the following pages.

PAGES:
{pages_text}

INSTRUCTIONS:
1. Find where § {rule_number} starts
2. Extract ALL content for § {rule_number} including:
   - Rule title and number
   - Complete explanation
   - All examples (Devanagari + IAST)
   - Footnotes and references
   - Related sub-sections
3. Determine where § {rule_number} ends (before next rule/section)
4. Output format:
   - Line 1: JSON: {{"end_page": N}}
   - Lines 2+: Complete markdown for rule § {rule_number}

IMPORTANT:
- If pages contain combined headers like "§ {rule_number}-{rule_number+1}", extract ONLY § {rule_number}
- Preserve all @deva[...] and @[...] tags exactly
- Include proper YAML front matter with metadata
- Stop at the boundary of § {rule_number} (don't include next rule)

Begin extraction:"""

    @staticmethod
    def extract_appendix(
        appendix_name: str,
        pages_content: List[str],
        start_page: int,
    ) -> str:
        """
        Generate prompt for extracting an appendix section

        Args:
            appendix_name: Name of appendix (e.g., "Prosody", "Dhātukośa")
            pages_content: List of page contents
            start_page: Starting page number

        Returns:
            Formatted prompt string
        """
        pages_text = "\n\n---PAGE_BREAK---\n\n".join(
            f"=== PAGE {start_page + i} ===\n{content}"
            for i, content in enumerate(pages_content)
        )

        return f"""Extract the {appendix_name} appendix from the following pages.

PAGES:
{pages_text}

INSTRUCTIONS:
1. Extract the complete {appendix_name} appendix
2. Format as markdown table where applicable:
   - Column headers for term, class, meaning, etc.
   - One entry per row
3. Preserve Sanskrit terms: Devanagari + IAST
4. Include all definitions, examples, cross-references
5. Add YAML front matter with appendix metadata

Output the complete appendix in structured markdown format.

Begin extraction:"""

    @staticmethod
    def verify_rule(
        rule_number: int,
        extracted_content: str,
        original_pages: List[str],
    ) -> str:
        """
        Generate prompt for verifying extracted rule quality

        Args:
            rule_number: Rule number
            extracted_content: Previously extracted content
            original_pages: Original page contents

        Returns:
            Verification prompt
        """
        return f"""Verify the extracted content for rule § {rule_number}.

EXTRACTED CONTENT:
{extracted_content}

ORIGINAL PAGES:
{chr(10).join(original_pages[:3])}  # Show first 3 pages

VERIFICATION TASKS:
1. Confirm rule number is correct
2. Check if extraction is complete (no missing parts)
3. Verify Devanagari and IAST are properly tagged
4. Check footnotes are included
5. Confirm it stops at the right boundary

Output:
- Line 1: JSON: {{"valid": true/false, "confidence": 0.0-1.0}}
- Line 2+: Issues found (if any) or "Verification passed"
"""

    @staticmethod
    def find_rule_pages(rule_number: int, available_pages: List[int]) -> str:
        """
        Generate prompt to find which pages contain a specific rule

        Args:
            rule_number: Rule to find
            available_pages: List of available page numbers

        Returns:
            Search prompt
        """
        return f"""Find which pages contain rule § {rule_number}.

Available pages: {min(available_pages)} to {max(available_pages)}

Search strategy:
1. Start from page containing rule § {rule_number - 1} if known
2. Otherwise search sequentially
3. Look for "§ {rule_number}" or "§§ {rule_number}"

Output: JSON with {{"start_page": N, "estimated_pages_needed": M}}"""
