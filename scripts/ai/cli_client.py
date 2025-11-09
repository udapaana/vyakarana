"""
Claude CLI client using terminal-based claude command
Works with Claude Pro/Max subscription instead of API
"""

import subprocess
import json
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class Message:
    """Single message in a conversation"""
    role: str  # 'user' or 'assistant'
    content: str

    def to_dict(self):
        return {"role": self.role, "content": self.content}


class ClaudeCLIClient:
    """
    Claude CLI client using terminal `claude` command

    Features:
    - Uses Claude Pro/Max subscription (no API costs)
    - Runs claude command via subprocess
    - No rate limits (subscription-based)
    - Simple text-based interface
    """

    def __init__(self):
        """Initialize CLI client"""
        # Check if claude command is available
        try:
            result = subprocess.run(
                ['claude', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError("claude CLI not found. Install from: https://claude.ai/download")
        except FileNotFoundError:
            raise RuntimeError("claude CLI not found. Install from: https://claude.ai/download")

    def chat(
        self,
        messages: List[Message],
        system: Optional[str] = None,
        stream: bool = False,
    ) -> str:
        """
        Send messages to Claude via CLI

        Args:
            messages: List of Message objects
            system: Optional system prompt
            stream: Ignored for CLI (always outputs directly)

        Returns:
            Assistant's response text
        """
        # Build the prompt
        prompt_parts = []

        # Add system prompt if provided
        if system:
            prompt_parts.append(f"<system>\n{system}\n</system>\n")

        # Add messages
        for msg in messages:
            if msg.role == "user":
                prompt_parts.append(msg.content)
            elif msg.role == "assistant":
                prompt_parts.append(f"Assistant: {msg.content}")

        full_prompt = "\n\n".join(prompt_parts)

        # Run claude CLI command
        try:
            import os
            # Create environment without ANTHROPIC_API_KEY to use browser auth
            env = os.environ.copy()
            env.pop('ANTHROPIC_API_KEY', None)

            result = subprocess.run(
                ['claude', '--print'],
                input=full_prompt,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                env=env  # Use environment without API key
            )

            if result.returncode != 0:
                raise RuntimeError(f"claude CLI error: {result.stderr}")

            return result.stdout.strip()

        except subprocess.TimeoutExpired:
            raise RuntimeError("claude CLI timeout (5 minutes)")
        except Exception as e:
            raise RuntimeError(f"claude CLI error: {e}")

    def get_usage_stats(self):
        """CLI doesn't track usage - return zeros"""
        return {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }

    def reset_usage_stats(self):
        """No-op for CLI client"""
        pass


class CLIClaudeClient(ClaudeCLIClient):
    """Alias for compatibility with existing code"""
    pass
