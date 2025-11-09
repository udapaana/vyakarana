#!/usr/bin/env python3
import subprocess
import yaml
import json
import re
from pathlib import Path

class CLIRuleExtractor:
    def __init__(self, pages_dir, output_dir):
        self.pages_dir = Path(pages_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.all_pages = sorted(self.pages_dir.glob("page_*.md"), key=lambda p: int(p.stem.split("_")[1]))
        print(f"Found {len(self.all_pages)} pages")

    def read_pages(self, start, count=5):
        content, nums = [], []
        for p in self.all_pages:
            n = int(p.stem.split("_")[1])
            if n < start: continue
            if n >= start + count: break
            content.append(f"=== PAGE {n} ===\n{p.read_text()}\n")
            nums.append(n)
        return "\n".join(content), nums

    def call_cli(self, prompt):
        # Use local Claude Code instance (this is running inside Claude Code already)
        # We're calling ourselves recursively, so this should work
        r = subprocess.run(["claude", "--print", "--output-format", "text", "--model", "sonnet"],
                          input=prompt, capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            raise RuntimeError(f"CLI failed (code {r.returncode}):\nSTDERR: {r.stderr}\nSTDOUT: {r.stdout}")
        return r.stdout.strip()

    def extract(self, num, start_page, max_pages=10):
        print(f"\n📖 Rule {num} from page {start_page}")
        pages, page_nums = self.read_pages(start_page, max_pages)

        prompt = f"""Extract rule section-{num} from Kale's Sanskrit Grammar.

Pages:
{pages}

Find rule section-{num} (header "## section-{num}"), extract complete content, stop at section-{num+1}.

Return ONLY JSON:
{{"rule_content": "...", "end_page": N, "source_pages": [...], "notes": "..."}}"""

        print("   ⏳ Calling Claude...")
        resp = self.call_cli(prompt)

        m = re.search(r'```json\s*(\{.*?\})\s*```', resp, re.DOTALL)
        if not m: m = re.search(r'\{.*\}', resp, re.DOTALL)
        if not m: raise ValueError(f"No JSON in response: {resp[:300]}")

        data = json.loads(m.group(1) if m.lastindex else m.group(0))
        print(f"   ✓ {len(data['rule_content'])} chars, pages {data['source_pages']}, ends {data['end_page']}")
        return data['rule_content'], data['end_page'], data['source_pages']

    def write(self, num, content, pages):
        f = self.output_dir / f"rule_{num}.md"
        with open(f, "w") as out:
            out.write("---\n")
            out.write(yaml.dump({"rule": f"§ {num}", "source_pages": pages}, allow_unicode=True))
            out.write("---\n\n" + content)
        print(f"   💾 {f}")

    def extract_all(self, start=1, end=972):
        print(f"\n🚀 Extracting rules {start}-{end}\n")
        page = 1
        for n in range(start, end + 1):
            try:
                content, end_page, pages = self.extract(n, page)
                self.write(n, content, pages)
                page = end_page
                if n % 10 == 0: print(f"\n📊 {n}/{end} ({100*(n-start+1)/(end-start+1):.1f}%)\n")
            except Exception as e:
                print(f"   ❌ Error: {e}")
                page += 1
                if page > 700: break
        print(f"\n✅ Done")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--start", type=int, default=1)
    p.add_argument("--end", type=int, default=972)
    p.add_argument("--output", default="rules_test")
    args = p.parse_args()

    base = Path("/Users/skmnktl/Downloads/ocr")
    CLIRuleExtractor(base / "structured_pages", base / args.output).extract_all(args.start, args.end)
