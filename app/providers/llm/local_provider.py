from __future__ import annotations

import requests

from app.core.config import settings
from app.providers.llm.base import LLMProvider


class LocalLLMProvider(LLMProvider):
    """
    Generic Ollama LLM provider skeleton.

    NOTE:
    This currently assumes an Ollama chat completions endpoint shape:
    POST /api/chat
    {
      "model": "...",
      "messages": [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."}
      ]
    }

    Response:
    {
      "message": [
        {
            "role": "assistant",
            "content": "...",
            "thinking: "..."
        }
      ]
    }

    If you use a different provider, update only this file.
    """

    def __init__(self):
        if not settings.llm_api_key:
            raise ValueError("LLM_API_KEY is not configured")

        self.api_key = settings.llm_api_key
        self.api_url = settings.llm_api_url
        self.model = settings.llm_model

    def generate(
            self,
            system_prompt: str,
            user_prompt: str,
    ) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "options": {
                "temperature": 0.2,
            }
        }

        headers = {
            "Content-Type": "application/json",
        }

        response = requests.post(
            self.api_url,
            headers=headers,
            json=payload,
            timeout=60,
        )
        response.raise_for_status()

        data = response.json()

        # Ollama response parsing
        return data["message"]["content"].strip()
