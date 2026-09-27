"""
Base Abstract Interface for LLM Providers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import httpx


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM foundation model integrations."""

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        """Lazily instantiate or return persistent AsyncClient with connection pooling."""
        if self._client is None or self._client.is_closed:
            limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
            self._client = httpx.AsyncClient(limits=limits)
        return self._client

    async def close(self) -> None:
        """Gracefully close the persistent client session."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if provider credentials and network endpoints are accessible."""
        pass

    @abstractmethod
    async def generate_response(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """Generate a raw text response from the model."""
        pass
