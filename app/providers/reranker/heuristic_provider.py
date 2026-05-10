from __future__ import annotations

import re

from app.providers.reranker.base import RerankerProvider
from app.services.retrieval_service import RetrievedChunk


class HeuristicRerankerProvider(RerankerProvider):
    """
    Week 6 heuristic reranker:
    Combines:
    - original semantic retrieval score
    - lexical token overlap
    - document title overlap
    - simple phrase containment boost

    This is intentionally lightweight and easy to explain.
    """

    def rerank(
            self,
            query: str,
            chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        if not chunks:
            return []

        query_tokens = self._tokenize(query)
        query_token_set = set(query_tokens)
        normalized_query = " ".join(query_tokens)

        scored: list[tuple[float, RetrievedChunk]] = []

        for chunk in chunks:
            content_tokens = self._tokenize(chunk.content)
            content_token_set = set(content_tokens)

            title_tokens = self._tokenize(chunk.document_title)
            title_token_set = set(title_tokens)

            lexical_overlap = self._overlap_ratio(query_token_set, content_token_set)
            title_overlap = self._overlap_ratio(query_token_set, title_token_set)

            normalized_content = " ".join(content_tokens)

            phrase_boost = 0.0
            if normalized_query and normalized_query in normalized_content:
                phrase_boost = 0.15

            combined_score = (
                    0.60 * chunk.score +       # semantic retrieval remains primary
                    0.25 * lexical_overlap +   # lexical precision
                    0.10 * title_overlap +     # doc title signal
                    phrase_boost               # exact-ish phrase bonus
            )

            scored.append((combined_score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)

        # Return chunks in reranked order
        return [chunk for _, chunk in scored]

    def _tokenize(self, text: str) -> list[str]:
        tokens = re.findall(r"[a-zA-Z0-9_]+", text.lower())
        return [t for t in tokens if len(t) > 1]

    def _overlap_ratio(self, a: set[str], b: set[str]) -> float:
        if not a or not b:
            return 0.0
        return len(a & b) / max(1, len(a))
