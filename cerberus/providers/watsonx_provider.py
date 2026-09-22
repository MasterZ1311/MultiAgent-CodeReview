"""
IBM watsonx Foundation Model Provider.
Integrates with IBM watsonx Orchestrate / watsonx.ai foundation models.
"""

import logging
from typing import Optional
import httpx
from cerberus.config import settings
from cerberus.providers.base import BaseLLMProvider

logger = logging.getLogger("cerberus.providers.watsonx")


class WatsonxProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = settings.WATSONX_API_KEY
        self.project_id = settings.WATSONX_PROJECT_ID
        self.endpoint = settings.WATSONX_URL

    async def is_available(self) -> bool:
        return bool(self.api_key and self.project_id)

    async def generate_response(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        if not await self.is_available():
            logger.debug("IBM watsonx credentials not configured; deferring to heuristic evaluator.")
            return None

        try:
            # Example watsonx text generation request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model_id": "ibm/granite-13b-chat-v2",
                "project_id": self.project_id,
                "input": f"System: {system_prompt}\n\nUser: {user_prompt}",
                "parameters": {
                    "decoding_method": "greedy",
                    "max_new_tokens": 1024,
                    "temperature": 0.1
                }
            }
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(f"{self.endpoint}/v1/generate", json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    return data.get("results", [{}])[0].get("generated_text")
        except Exception as e:
            logger.warning(f"watsonx API request failed: {e}")
        return None
