"""
Claude CLI Wrapper for OCR Rule Extraction

A modular AI interface for Phase 3 rule extraction from Kale's Sanskrit Grammar.
"""

from .client import ClaudeClient
from .conversation import ConversationManager
from .prompts import PromptTemplates
from .batch import BatchProcessor
from .tracker import CostTracker

__all__ = [
    'ClaudeClient',
    'ConversationManager',
    'PromptTemplates',
    'BatchProcessor',
    'CostTracker',
]

__version__ = '1.0.0'
