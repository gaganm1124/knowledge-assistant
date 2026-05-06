from __future__ import annotations

from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.providers.embeddings.base import EmbeddingProvider


class LocalEmbeddingProvider(EmbeddingProvider):
    """
    Local embedding provider using SentenceTransformers.

    Recommended model for this project:
      - BAAI/bge-base-en-v1.5   (768 dims)

    Notes:
    - Uses GPU automatically if available.
    - Normalizes embeddings so cosine similarity behaves well.
    """

    def __init__(self):
        model_name = getattr(settings, "embedding_model", "BAAI/bge-base-en-v1.5")
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True,   # important for cosine similarity
            convert_to_numpy=True,
        )

        return embeddings.tolist()
