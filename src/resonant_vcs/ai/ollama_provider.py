"""Ollama AI provider implementation."""

import httpx
import time
from typing import Optional

from .base import AIProvider, AIResponse


class OllamaProvider(AIProvider):
    """Ollama local AI provider."""

    DEFAULT_BASE_URL = "http://localhost:11434"
    DEFAULT_MODEL = "llama3.2"

    def __init__(self, model: str = DEFAULT_MODEL, base_url: str = DEFAULT_BASE_URL):
        super().__init__(model)
        self.base_url = base_url.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=self.base_url, timeout=60.0)
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            import httpx
            import asyncio
            client = httpx.Client(base_url=self.base_url, timeout=5.0)
            response = client.get("/api/tags")
            client.close()
            return response.status_code == 200
        except Exception:
            return False

    def get_name(self) -> str:
        """Get the provider name."""
        return "ollama"

    async def generate(self, prompt: str, **kwargs) -> AIResponse:
        """Generate a response using Ollama."""
        start = time.time()
        client = await self._get_client()

        try:
            response = await client.post(
                "/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    **kwargs
                }
            )
            latency = (time.time() - start) * 1000

            if response.status_code == 200:
                data = response.json()
                return AIResponse(
                    content=data.get("response", ""),
                    model=self.model,
                    provider="ollama",
                    latency_ms=latency
                )
            else:
                return AIResponse(
                    content="",
                    model=self.model,
                    provider="ollama",
                    latency_ms=latency,
                    error=f"HTTP {response.status_code}: {response.text}"
                )

        except httpx.ConnectError:
            return AIResponse(
                content="",
                model=self.model,
                provider="ollama",
                latency_ms=(time.time() - start) * 1000,
                error="Cannot connect to Ollama. Is it running?"
            )
        except Exception as e:
            return AIResponse(
                content="",
                model=self.model,
                provider="ollama",
                latency_ms=(time.time() - start) * 1000,
                error=str(e)
            )


class OllamaProviderSync(OllamaProvider):
    """Synchronous wrapper for Ollama provider."""

    def generate(self, prompt: str, **kwargs) -> AIResponse:
        """Synchronous generate."""
        import httpx
        start = time.time()

        try:
            client = httpx.Client(base_url=self.base_url, timeout=60.0)
            response = client.post(
                "/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    **kwargs
                }
            )
            latency = (time.time() - start) * 1000
            client.close()

            if response.status_code == 200:
                data = response.json()
                return AIResponse(
                    content=data.get("response", ""),
                    model=self.model,
                    provider="ollama",
                    latency_ms=latency
                )
            else:
                return AIResponse(
                    content="",
                    model=self.model,
                    provider="ollama",
                    latency_ms=latency,
                    error=f"HTTP {response.status_code}"
                )

        except Exception as e:
            return AIResponse(
                content="",
                model=self.model,
                provider="ollama",
                latency_ms=(time.time() - start) * 1000,
                error=str(e)
            )