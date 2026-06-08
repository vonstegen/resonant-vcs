"""Abstract base class for AI providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class AIResponse:
    """Response from an AI provider."""
    content: str
    model: str
    provider: str
    latency_ms: float = 0.0
    error: Optional[str] = None


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    def __init__(self, model: str = "llama3.2"):
        self.model = model

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> AIResponse:
        """Generate a response from the AI."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get the provider name."""
        pass