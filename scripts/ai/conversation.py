"""
Conversation Manager for maintaining context across API calls
"""

import json
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
from .client import Message


class ConversationManager:
    """
    Manages conversation history and context

    Features:
    - Save/load conversation history
    - Context window management
    - Conversation templates
    - Metadata tracking
    """

    def __init__(self, max_history: int = 10):
        """
        Initialize conversation manager

        Args:
            max_history: Maximum number of message pairs to keep
        """
        self.messages: List[Message] = []
        self.max_history = max_history
        self.metadata: Dict = {
            "created_at": datetime.utcnow().isoformat(),
            "message_count": 0,
        }

    def add_message(self, role: str, content: str):
        """Add a message to the conversation"""
        self.messages.append(Message(role=role, content=content))
        self.metadata["message_count"] += 1

        # Trim history if needed (keep system messages)
        if len(self.messages) > self.max_history * 2:
            # Keep first message if it's a system instruction
            if self.messages[0].role == "user":
                self.messages = [self.messages[0]] + self.messages[-(self.max_history * 2):]
            else:
                self.messages = self.messages[-(self.max_history * 2):]

    def add_user_message(self, content: str):
        """Convenience method for user messages"""
        self.add_message("user", content)

    def add_assistant_message(self, content: str):
        """Convenience method for assistant messages"""
        self.add_message("assistant", content)

    def get_messages(self) -> List[Message]:
        """Get all messages"""
        return self.messages

    def clear(self):
        """Clear conversation history"""
        self.messages = []
        self.metadata["message_count"] = 0

    def save(self, filepath: Path):
        """Save conversation to JSON file"""
        data = {
            "metadata": self.metadata,
            "messages": [m.to_dict() for m in self.messages],
        }

        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load(self, filepath: Path):
        """Load conversation from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.metadata = data.get("metadata", {})
        self.messages = [
            Message(role=m["role"], content=m["content"])
            for m in data.get("messages", [])
        ]

    def to_dict(self) -> Dict:
        """Export conversation as dictionary"""
        return {
            "metadata": self.metadata,
            "messages": [m.to_dict() for m in self.messages],
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ConversationManager':
        """Create conversation from dictionary"""
        conv = cls()
        conv.metadata = data.get("metadata", {})
        conv.messages = [
            Message(role=m["role"], content=m["content"])
            for m in data.get("messages", [])
        ]
        return conv
