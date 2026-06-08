"""AI module for AugmentedVCS."""

from .base import AIProvider, AIResponse
from .ollama_provider import OllamaProvider, OllamaProviderSync
from .switcher import AISwitcher, AIConfig, get_switcher
from .intent import IntentClassifier, IntentMapper, VCSIntent, ParsedIntent
from .features import CommitSuggester, ChangesSummarizer, VersionNarrator

__all__ = [
    "AIProvider",
    "AIResponse", 
    "OllamaProvider",
    "OllamaProviderSync",
    "AISwitcher",
    "AIConfig",
    "get_switcher",
    "IntentClassifier",
    "IntentMapper",
    "VCSIntent",
    "ParsedIntent",
    "CommitSuggester",
    "ChangesSummarizer",
    "VersionNarrator",
]
