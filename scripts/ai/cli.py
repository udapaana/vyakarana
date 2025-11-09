#!/usr/bin/env python3
"""
Command-line interface for Claude AI wrapper

Usage:
    # Extract all rules
    python -m scripts.ai.cli extract-all --output rules_llm

    # Extract specific range
    python -m scripts.ai.cli extract-range 1 50 --output rules_test

    # Extract single rule
    python -m scripts.ai.cli extract-one 77 --output rules_test

    # Interactive chat
    python -m scripts.ai.cli chat

    # Verify extraction
    python -m scripts.ai.cli verify 77
"""

import argparse
import sys
from pathlib import Path

from .client import ClaudeClient
from .conversation import ConversationManager
from .prompts import PromptTemplates
from .batch import BatchProcessor
from .tracker import CostTracker


def cmd_extract_all(args):
    """Extract all 972 rules"""
    output_dir = Path(args.output)
    structured_pages = Path(args.pages) if args.pages else Path("structured_pages")

    print(f"📚 Extracting all 972 rules")
    print(f"📁 Input: {structured_pages}")
    print(f"📁 Output: {output_dir}")

    # Initialize components
    client = ClaudeClient(model=args.model)
    tracker = CostTracker(model=args.model)
    processor = BatchProcessor(
        structured_pages_dir=structured_pages,
        output_dir=output_dir,
        client=client,
        tracker=tracker,
    )

    # Process all rules
    processor.process_batch(start_rule=1, end_rule=972)

    # Save tracking data
    tracker_file = output_dir / "usage_stats.json"
    tracker.save(tracker_file)
    print(f"💾 Usage stats saved to {tracker_file}")


def cmd_extract_range(args):
    """Extract a range of rules"""
    start, end = args.start, args.end
    output_dir = Path(args.output)
    structured_pages = Path(args.pages) if args.pages else Path("structured_pages")

    print(f"📚 Extracting rules {start}-{end}")
    print(f"📁 Input: {structured_pages}")
    print(f"📁 Output: {output_dir}")

    # Initialize components
    client = ClaudeClient(model=args.model)
    tracker = CostTracker(model=args.model)
    processor = BatchProcessor(
        structured_pages_dir=structured_pages,
        output_dir=output_dir,
        client=client,
        tracker=tracker,
    )

    # Process range
    processor.process_batch(start_rule=start, end_rule=end)

    # Save tracking data
    tracker_file = output_dir / "usage_stats.json"
    tracker.save(tracker_file)
    print(f"💾 Usage stats saved to {tracker_file}")


def cmd_extract_one(args):
    """Extract a single rule"""
    rule_num = args.rule
    output_dir = Path(args.output)
    structured_pages = Path(args.pages) if args.pages else Path("structured_pages")

    print(f"📚 Extracting rule {rule_num}")

    # Initialize components
    client = ClaudeClient(model=args.model)
    tracker = CostTracker(model=args.model)
    processor = BatchProcessor(
        structured_pages_dir=structured_pages,
        output_dir=output_dir,
        client=client,
        tracker=tracker,
    )

    # Extract single rule
    result = processor.extract_rule(
        rule_number=rule_num,
        start_page=args.start_page or 1,
    )

    if result.success:
        processor.save_rule(result)
        print(f"✓ Rule {rule_num} extracted successfully")
        print(f"  End page: {result.end_page}")
        print(f"  Output: {output_dir / f'rule_{rule_num:03d}.md'}")
    else:
        print(f"✗ Failed to extract rule {rule_num}: {result.error}")
        sys.exit(1)

    tracker.print_summary()


def cmd_chat(args):
    """Interactive chat mode"""
    print("💬 Claude Chat Mode")
    print("Type 'exit' or 'quit' to end\n")

    client = ClaudeClient(model=args.model)
    conv = ConversationManager()

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ['exit', 'quit']:
                break

            if not user_input:
                continue

            conv.add_user_message(user_input)

            print("Claude: ", end="")
            response = client.chat(
                messages=conv.get_messages(),
                stream=True,  # Streaming for interactive feel
            )

            conv.add_assistant_message(response)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def cmd_verify(args):
    """Verify extracted rule"""
    rule_num = args.rule
    rules_dir = Path(args.rules_dir)
    structured_pages = Path(args.pages) if args.pages else Path("structured_pages")

    rule_file = rules_dir / f"rule_{rule_num:03d}.md"
    if not rule_file.exists():
        print(f"❌ Rule file not found: {rule_file}")
        sys.exit(1)

    print(f"🔍 Verifying rule {rule_num}")

    # Read extracted content
    with open(rule_file, 'r', encoding='utf-8') as f:
        extracted = f.read()

    # Read original pages (estimate 3 pages)
    pages = []
    for i in range(3):
        page_file = structured_pages / f"page_{args.start_page + i:03d}.md"
        if page_file.exists():
            with open(page_file, 'r', encoding='utf-8') as f:
                pages.append(f.read())

    # Create verification prompt
    prompt = PromptTemplates.verify_rule(rule_num, extracted, pages)

    client = ClaudeClient(model=args.model)
    conv = ConversationManager()
    conv.add_user_message(prompt)

    print("\nVerification Result:")
    print("-" * 60)
    response = client.chat(messages=conv.get_messages(), stream=True)
    print("-" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Claude CLI Wrapper for Rule Extraction"
    )
    parser.add_argument(
        '--model',
        default='claude-sonnet-4-20250514',
        help='Claude model to use'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # extract-all command
    p_all = subparsers.add_parser('extract-all', help='Extract all 972 rules')
    p_all.add_argument('--output', default='rules_llm', help='Output directory')
    p_all.add_argument('--pages', help='Structured pages directory')

    # extract-range command
    p_range = subparsers.add_parser('extract-range', help='Extract range of rules')
    p_range.add_argument('start', type=int, help='Start rule number')
    p_range.add_argument('end', type=int, help='End rule number')
    p_range.add_argument('--output', default='rules_llm', help='Output directory')
    p_range.add_argument('--pages', help='Structured pages directory')

    # extract-one command
    p_one = subparsers.add_parser('extract-one', help='Extract single rule')
    p_one.add_argument('rule', type=int, help='Rule number')
    p_one.add_argument('--output', default='rules_test', help='Output directory')
    p_one.add_argument('--pages', help='Structured pages directory')
    p_one.add_argument('--start-page', type=int, help='Starting page number')

    # chat command
    p_chat = subparsers.add_parser('chat', help='Interactive chat mode')

    # verify command
    p_verify = subparsers.add_parser('verify', help='Verify extracted rule')
    p_verify.add_argument('rule', type=int, help='Rule number to verify')
    p_verify.add_argument('--rules-dir', default='rules_llm', help='Rules directory')
    p_verify.add_argument('--pages', help='Structured pages directory')
    p_verify.add_argument('--start-page', type=int, default=1, help='Starting page')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Route to command handler
    commands = {
        'extract-all': cmd_extract_all,
        'extract-range': cmd_extract_range,
        'extract-one': cmd_extract_one,
        'chat': cmd_chat,
        'verify': cmd_verify,
    }

    commands[args.command](args)


if __name__ == '__main__':
    main()
