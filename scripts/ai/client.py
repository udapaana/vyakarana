"""
Core Claude API Client with streaming support
"""

import os
import json
import time
from typing import Optional, Dict, List, Generator, Any
from anthropic import Anthropic, APIError, RateLimitError
from dataclasses import dataclass


@dataclass
class Message:
    """Single message in a conversation"""
    role: str  # 'user' or 'assistant'
    content: str

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}


class ClaudeClient:
    """
    Core Claude API client with streaming and error handling

    Features:
    - Streaming responses for real-time output
    - Automatic retry with exponential backoff
    - Rate limit handling
    - Token usage tracking
    - Conversation history management
    """

    DEFAULT_MODEL = "claude-sonnet-4-20250514"
    DEFAULT_MAX_TOKENS = 4096

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = 0.0,
    ):
        """
        Initialize Claude client

        Args:
            api_key: Anthropic API key (or from ANTHROPIC_API_KEY env)
            model: Claude model to use
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0 = deterministic)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("API key required: set ANTHROPIC_API_KEY or pass api_key")

        self.client = Anthropic(api_key=self.api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

        # Token usage tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def chat(
        self,
        messages: List[Message],
        system: Optional[str] = None,
        stream: bool = False,
        max_retries: int = 3,
    ) -> str:
        """
        Send messages to Claude and get response

        Args:
            messages: List of Message objects
            system: Optional system prompt
            stream: Enable streaming output
            max_retries: Number of retries on failure

        Returns:
            Assistant's response text
        """
        for attempt in range(max_retries):
            try:
                if stream:
                    return self._chat_streaming(messages, system)
                else:
                    return self._chat_blocking(messages, system)

            except RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"\n⚠️  Rate limited. Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    raise

            except APIError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"\n⚠️  API error: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise

    def _chat_blocking(
        self,
        messages: List[Message],
        system: Optional[str] = None,
    ) -> str:
        """Non-streaming chat"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system if system else [],
            messages=[m.to_dict() for m in messages],
        )

        # Track token usage
        self.total_input_tokens += response.usage.input_tokens
        self.total_output_tokens += response.usage.output_tokens

        return response.content[0].text

    def _chat_streaming(
        self,
        messages: List[Message],
        system: Optional[str] = None,
    ) -> str:
        """Streaming chat with real-time output"""
        full_response = ""

        with self.client.messages.stream(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system if system else [],
            messages=[m.to_dict() for m in messages],
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                full_response += text

        print()  # Newline after streaming

        # Track token usage from final message
        final_message = stream.get_final_message()
        self.total_input_tokens += final_message.usage.input_tokens
        self.total_output_tokens += final_message.usage.output_tokens

        return full_response

    def get_usage_stats(self) -> Dict[str, int]:
        """Get token usage statistics"""
        return {
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
        }

    def reset_usage_stats(self):
        """Reset token usage counters"""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
