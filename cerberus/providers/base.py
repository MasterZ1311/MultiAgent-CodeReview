"""
Base Abstract Interface for LLM Providers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM foundation model integrations."""

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if provider credentials and network endpoints are accessible."""
        pass

    @abstractmethod
    async def generate_response(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """Generate a raw text response from the model."""
        pass
