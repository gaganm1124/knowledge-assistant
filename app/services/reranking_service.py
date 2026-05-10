from __future__ import annotations

from app.providers.reranker.base import RerankerProvider
from app.services.retrieval_service import RetrievedChunk


class RerankingService:
    """
    Thin wrapper around the reranker provider.
    """

    def __init__(self, provider: RerankerProvider):
        self.provider = provider

    def rerank(
            self,
            query: str,
            chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        if not chunks:
            return []
        return self.provider.rerank(query=query, chunks=chunks)
