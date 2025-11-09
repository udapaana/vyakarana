#!/usr/bin/env python3
"""
Test script for Claude AI wrapper

Tests the extraction system with a few sample rules
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.ai.client import ClaudeClient
from scripts.ai.batch import BatchProcessor
from scripts.ai.tracker import CostTracker


def test_single_rule():
    """Test extracting a single rule"""
    print("\n" + "="*60)
    print("TEST 1: Extract Rule 77")
    print("="*60)

    client = ClaudeClient()
    tracker = CostTracker()

    processor = BatchProcessor(
        structured_pages_dir=Path("structured_pages"),
        output_dir=Path("rules_test"),
        client=client,
        tracker=tracker,
    )

    # Extract rule 77 (from page 50)
    result = processor.extract_rule(
        rule_number=77,
        start_page=50,
        max_pages=5,
    )

    if result.success:
        print(f"✓ Successfully extracted rule 77")
        print(f"  End page: {result.end_page}")
        print(f"  Content length: {len(result.content)} chars")

        # Save the result
        processor.save_rule(result)
        print(f"  Saved to: rules_test/rule_077.md")

        # Show snippet
        print(f"\nContent snippet:")
        print("-" * 60)
        print(result.content[:500] + "...")
        print("-" * 60)
    else:
        print(f"✗ Failed: {result.error}")
        return False

    tracker.print_summary()
    return True


def test_batch_extraction():
    """Test extracting multiple rules"""
    print("\n" + "="*60)
    print("TEST 2: Extract Rules 1-5")
    print("="*60)

    client = ClaudeClient()
    tracker = CostTracker()

    processor = BatchProcessor(
        structured_pages_dir=Path("structured_pages"),
        output_dir=Path("rules_test"),
        client=client,
        tracker=tracker,
    )

    # Extract first 5 rules
    processor.process_batch(start_rule=1, end_rule=5)

    # Check results
    success_count = 0
    for i in range(1, 6):
        rule_file = Path(f"rules_test/rule_{i:03d}.md")
        if rule_file.exists():
            success_count += 1
            size = rule_file.stat().st_size
            print(f"  ✓ rule_{i:03d}.md ({size} bytes)")
        else:
            print(f"  ✗ rule_{i:03d}.md (missing)")

    print(f"\nSuccessfully extracted {success_count}/5 rules")
    tracker.print_summary()

    return success_count == 5


def test_conversation():
    """Test conversation management"""
    print("\n" + "="*60)
    print("TEST 3: Conversation Management")
    print("="*60)

    from scripts.ai.conversation import ConversationManager

    conv = ConversationManager()
    conv.add_user_message("What is Sanskrit grammar?")
    conv.add_assistant_message("Sanskrit grammar is the systematic study...")
    conv.add_user_message("Tell me more about Panini")

    print(f"Messages in conversation: {len(conv.get_messages())}")

    # Test save/load
    test_file = Path("rules_test/test_conversation.json")
    conv.save(test_file)
    print(f"✓ Saved conversation to {test_file}")

    conv2 = ConversationManager()
    conv2.load(test_file)
    print(f"✓ Loaded conversation: {len(conv2.get_messages())} messages")

    return len(conv2.get_messages()) == len(conv.get_messages())


def test_prompts():
    """Test prompt templates"""
    print("\n" + "="*60)
    print("TEST 4: Prompt Templates")
    print("="*60)

    from scripts.ai.prompts import PromptTemplates

    # Test rule extraction prompt
    pages = ["Page content 1", "Page content 2"]
    prompt = PromptTemplates.extract_rule(
        rule_number=77,
        pages_content=pages,
        start_page=50,
    )

    print(f"✓ Generated extraction prompt ({len(prompt)} chars)")
    print(f"  Contains rule number: {('§ 77' in prompt)}")
    print(f"  Contains page markers: {('PAGE_BREAK' in prompt)}")

    # Test system prompt
    system = PromptTemplates.SYSTEM_RULE_EXTRACTION
    print(f"✓ System prompt available ({len(system)} chars)")

    return True


def main():
    """Run all tests"""
    print("\n🧪 Testing Claude AI Wrapper")
    print("="*60)

    tests = [
        ("Prompt Templates", test_prompts),
        ("Conversation Management", test_conversation),
        ("Single Rule Extraction", test_single_rule),
        ("Batch Extraction", test_batch_extraction),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")

    passed = sum(1 for r in results.values() if r)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
