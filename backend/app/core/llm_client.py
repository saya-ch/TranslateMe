"""
LLM 调用客户端 - 支持 OpenAI 兼容 API
失败时回退到本地模板
"""

import json
import time
from typing import Optional, Dict, Any
import httpx
from app.config import settings


class LLMClient:
    def __init__(self):
        self.base_url = settings.LLM_API_BASE
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL
        self.timeout = settings.LLM_TIMEOUT_SECONDS
        self.fallback_enabled = settings.LLM_FALLBACK_ENABLED
        self.max_tokens = settings.LLM_MAX_TOKENS

    def is_configured(self) -> bool:
        return bool(self.api_key) and bool(self.base_url)

    async def generate_json(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        if not self.is_configured():
            return None

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url.rstrip('/')}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "temperature": 0.3,
                        "max_tokens": self.max_tokens,
                        "response_format": {"type": "json_object"},
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                    },
                )
                if response.status_code != 200:
                    return None

                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if not content:
                    return None

                parsed = json.loads(content)
                return parsed
        except Exception:
            return None


llm_client = LLMClient()
