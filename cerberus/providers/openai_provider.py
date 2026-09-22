"""
OpenAI & Azure Compatible LLM Provider.
"""

import logging
from typing import Optional
import httpx
from cerberus.config import settings
from cerberus.providers.base import BaseLLMProvider

logger = logging.getLogger("cerberus.providers.openai")


class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL

    async def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 10)

    async def generate_response(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        if not await self.is_available():
            return None

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.1
            }
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning(f"OpenAI completion failed: {e}")
        return None
