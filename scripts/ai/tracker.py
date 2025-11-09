"""
Cost and usage tracking for API calls
"""

import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class UsageStats:
    """Token usage statistics"""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    api_calls: int = 0

    def add(self, input_tokens: int, output_tokens: int):
        """Add tokens to statistics"""
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.total_tokens += input_tokens + output_tokens
        self.api_calls += 1


class CostTracker:
    """
    Track API costs and usage across sessions

    Features:
    - Token usage tracking
    - Cost estimation
    - Per-rule and total statistics
    - Persistent storage
    """

    # Pricing per million tokens (as of 2024)
    # Update these based on current Anthropic pricing
    PRICING = {
        "claude-sonnet-4-20250514": {
            "input": 3.00,   # $3 per million input tokens
            "output": 15.00, # $15 per million output tokens
        },
        "claude-sonnet-3-5-20241022": {
            "input": 3.00,
            "output": 15.00,
        },
    }

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        """
        Initialize cost tracker

        Args:
            model: Claude model being used
        """
        self.model = model
        self.session_stats = UsageStats()
        self.total_stats = UsageStats()
        self.rule_stats: Dict[int, UsageStats] = {}

        self.metadata = {
            "model": model,
            "session_start": datetime.utcnow().isoformat(),
        }

    def track_usage(
        self,
        input_tokens: int,
        output_tokens: int,
        rule_number: Optional[int] = None,
    ):
        """
        Track token usage for an API call

        Args:
            input_tokens: Input tokens used
            output_tokens: Output tokens used
            rule_number: Optional rule number for per-rule tracking
        """
        self.session_stats.add(input_tokens, output_tokens)
        self.total_stats.add(input_tokens, output_tokens)

        if rule_number is not None:
            if rule_number not in self.rule_stats:
                self.rule_stats[rule_number] = UsageStats()
            self.rule_stats[rule_number].add(input_tokens, output_tokens)

    def get_cost(self, stats: UsageStats) -> float:
        """Calculate cost for given usage statistics"""
        pricing = self.PRICING.get(self.model, self.PRICING["claude-sonnet-4-20250514"])

        input_cost = (stats.input_tokens / 1_000_000) * pricing["input"]
        output_cost = (stats.output_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost

    def get_session_cost(self) -> float:
        """Get cost for current session"""
        return self.get_cost(self.session_stats)

    def get_total_cost(self) -> float:
        """Get total cost across all sessions"""
        return self.get_cost(self.total_stats)

    def get_rule_cost(self, rule_number: int) -> float:
        """Get cost for specific rule"""
        if rule_number not in self.rule_stats:
            return 0.0
        return self.get_cost(self.rule_stats[rule_number])

    def print_summary(self):
        """Print usage summary"""
        print("\n" + "="*60)
        print("API USAGE SUMMARY")
        print("="*60)
        print(f"Model: {self.model}")
        print(f"\nSession Statistics:")
        print(f"  API Calls:     {self.session_stats.api_calls}")
        print(f"  Input Tokens:  {self.session_stats.input_tokens:,}")
        print(f"  Output Tokens: {self.session_stats.output_tokens:,}")
        print(f"  Total Tokens:  {self.session_stats.total_tokens:,}")
        print(f"  Estimated Cost: ${self.get_session_cost():.4f}")

        if self.total_stats.api_calls > self.session_stats.api_calls:
            print(f"\nTotal Statistics (All Sessions):")
            print(f"  API Calls:     {self.total_stats.api_calls}")
            print(f"  Total Tokens:  {self.total_stats.total_tokens:,}")
            print(f"  Estimated Cost: ${self.get_total_cost():.4f}")

        if self.rule_stats:
            print(f"\nRules Processed: {len(self.rule_stats)}")
            avg_cost = sum(self.get_rule_cost(n) for n in self.rule_stats) / len(self.rule_stats)
            print(f"Average Cost/Rule: ${avg_cost:.4f}")

        print("="*60 + "\n")

    def save(self, filepath: Path):
        """Save tracking data to JSON"""
        data = {
            "metadata": self.metadata,
            "session_stats": asdict(self.session_stats),
            "total_stats": asdict(self.total_stats),
            "rule_stats": {
                str(k): asdict(v) for k, v in self.rule_stats.items()
            },
        }

        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def load(self, filepath: Path):
        """Load tracking data from JSON"""
        if not filepath.exists():
            return

        with open(filepath, 'r') as f:
            data = json.load(f)

        self.metadata = data.get("metadata", self.metadata)
        self.total_stats = UsageStats(**data.get("total_stats", {}))
        self.rule_stats = {
            int(k): UsageStats(**v)
            for k, v in data.get("rule_stats", {}).items()
        }
