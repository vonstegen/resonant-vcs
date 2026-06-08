"""AI provider switcher and configuration."""

from typing import Optional
from dataclasses import dataclass, field

from .base import AIProvider, AIResponse
from .ollama_provider import OllamaProvider, OllamaProviderSync


@dataclass
class AIConfig:
    """Configuration for AI providers."""
    preferred_provider: str = "ollama"
    ollama_model: str = "llama3.2"
    ollama_base_url: str = "http://localhost:11434"
    fallback_enabled: bool = True
    timeout_seconds: int = 60


class AISwitcher:
    """Switch between AI providers with fallback support."""

    def __init__(self, config: Optional[AIConfig] = None):
        self.config = config or AIConfig()
        self._providers: dict[str, AIProvider] = {}
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize available providers."""
        # Ollama
        ollama = OllamaProviderSync(
            model=self.config.ollama_model,
            base_url=self.config.ollama_base_url
        )
        if ollama.is_available():
            self._providers["ollama"] = ollama

    def get_provider(self, name: Optional[str] = None) -> Optional[AIProvider]:
        """Get a provider by name."""
        if name:
            return self._providers.get(name)
        return self._providers.get(self.config.preferred_provider)

    def generate(self, prompt: str, provider_name: Optional[str] = None) -> AIResponse:
        """Generate using the specified or preferred provider."""
        provider = self.get_provider(provider_name)

        if not provider:
            return AIResponse(
                content="",
                model="",
                provider="none",
                error="No AI provider available. Install Ollama or configure a provider."
            )

        response = provider.generate(prompt)

        # Handle errors with fallback if enabled
        if response.error and self.config.fallback_enabled:
            for name, prov in self._providers.items():
                if name != provider_name:
                    fallback = prov.generate(prompt)
                    if not fallback.error:
                        return fallback

        return response

    def list_providers(self) -> list[str]:
        """List available provider names."""
        return list(self._providers.keys())

    def is_available(self) -> bool:
        """Check if any provider is available."""
        return len(self._providers) > 0

    def get_status(self) -> dict:
        """Get status of all providers."""
        status = {}
        for name, provider in self._providers.items():
            status[name] = {
                "available": True,
                "model": provider.model
            }
        # Add missing providers as unavailable
        for name in ["ollama"]:
            if name not in status:
                status[name] = {"available": False}
        return status


# Global instance
_default_switcher: Optional[AISwitcher] = None


def get_switcher(config: Optional[AIConfig] = None) -> AISwitcher:
    """Get the global AI switcher instance."""
    global _default_switcher
    if _default_switcher is None:
        _default_switcher = AISwitcher(config)
    return _default_switcher