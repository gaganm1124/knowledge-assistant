from __future__ import annotations

import requests

from app.core.config import settings
from app.providers.embeddings.base import EmbeddingProvider


class HostedEmbeddingProvider(EmbeddingProvider):
    """
    Generic hosted embedding provider skeleton.

    NOTE:
    This implementation currently assumes an OpenAI-compatible embeddings endpoint shape:
    POST /v1/embeddings
    {
      "model": "...",
      "input": ["text1", "text2"]
    }

    Response:
    {
      "data": [
        {"embedding": [...]},
        ...
      ]
    }

    If you use a different provider, update only this file.
    """

    def __init__(self):
        if not settings.embedding_api_key:
            raise ValueError("EMBEDDING_API_KEY is not configured")
        if not settings.embedding_api_url:
            raise ValueError("EMBEDDING_API_URL is not configured")

        self.api_key = settings.embedding_api_key
        self.api_url = settings.embedding_api_url
        self.model = settings.embedding_model

    def embed_text(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        payload = {
            "model": self.model,
            "input": texts,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            self.api_url,
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()

        # OpenAI-compatible response parsing
        embeddings = [item["embedding"] for item in data["data"]]

        return embeddings
