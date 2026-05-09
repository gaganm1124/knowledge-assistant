from __future__ import annotations

import logging
from pathlib import Path

from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.providers.embeddings.base import EmbeddingProvider

logger = logging.getLogger(__name__)


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
        cache_dir = getattr(settings, "embedding_cache_dir", "") or None
        model_kwargs = {}

        if cache_dir:
            Path(cache_dir).mkdir(parents=True, exist_ok=True)
            model_kwargs["cache_folder"] = cache_dir

        try:
            self.model = SentenceTransformer(
                model_name,
                local_files_only=True,
                **model_kwargs,
            )
            logger.info("Loaded SentenceTransformer model from local cache: %s", model_name)
        except Exception:
            logger.info(
                "SentenceTransformer model %s was not fully available in the local cache; "
                "downloading it into %s.",
                model_name,
                cache_dir or "the default cache",
            )
            logger.debug("Local cache load failed", exc_info=True)
            self.model = SentenceTransformer(model_name, **model_kwargs)

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
