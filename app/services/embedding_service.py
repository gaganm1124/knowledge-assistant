from __future__ import annotations

from app.providers.embeddings.base import EmbeddingProvider


class EmbeddingService:
    """
    Thin orchestration layer around the provider.
    Keeps provider-specific logic out of ingestion/retrieval services.
    """

    def __init__(self, provider: EmbeddingProvider):
        self.provider = provider

    def embed_text(self, text: str) -> list[float]:
        return self.provider.embed_text(text)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return self.provider.embed_texts(texts)
