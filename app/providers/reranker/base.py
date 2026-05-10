from __future__ import annotations

from typing import Protocol

from app.services.retrieval_service import RetrievedChunk


class RerankerProvider(Protocol):
    def rerank(
            self,
            query: str,
            chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        ...
