from __future__ import annotations

import httpx

from app.core.config import get_settings
from app.utils.errors import ServiceError


class QwenClient:
    def __init__(self) -> None:
        settings = get_settings()
        self._base_url = settings.qwen_base_url.rstrip("/")
        self._model_name = settings.qwen_model_name

    async def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        payload = {
            "model": self._model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
        }

        print("MODEL:", self._model_name)
        print("SYSTEM LEN:", len(system_prompt))
        print("USER LEN:", len(user_prompt))

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(f"{self._base_url}/v1/chat/completions", json=payload)
                if response.status_code != 200:
                    print(response.text)
                    response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ServiceError("Qwen generation failed") from exc

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ServiceError("Invalid Qwen response format") from exc
