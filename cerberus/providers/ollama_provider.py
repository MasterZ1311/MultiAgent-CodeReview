"""
Local Ollama LLM Provider for Air-Gapped & Privacy-Preserving Deployments.
"""

import logging
from typing import Optional
import httpx
from cerberus.config import settings
from cerberus.providers.base import BaseLLMProvider

logger = logging.getLogger("cerberus.providers.ollama")


class OllamaProvider(BaseLLMProvider):
    def __init__(self):
        super().__init__()
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL

    async def is_available(self) -> bool:
        try:
            client = await self.get_client()
            res = await client.get(f"{self.base_url}/api/tags", timeout=1.0)
            return res.status_code == 200
        except Exception:
            return False

    async def generate_response(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        try:
            payload = {
                "model": self.model,
                "prompt": f"{system_prompt}\n\n{user_prompt}",
                "stream": False
            }
            client = await self.get_client()
            res = await client.post(f"{self.base_url}/api/generate", json=payload, timeout=30.0)
            if res.status_code == 200:
                return res.json().get("response")
        except Exception as e:
            logger.warning(f"Ollama generation failed: {e}")
        return None
