from __future__ import annotations

import time
import uuid

from app.domain.schemas import QueryResponse
from app.services.citation_service import CitationService
from app.services.generation_service import GenerationService
from app.services.retrieval_service import RetrievalService


class QueryService:
    """
    Week 4 query orchestration:
    1. Retrieve chunks
    2. Apply simple fallback if nothing useful is found
    3. Generate grounded answer
    4. Build citations
    5. Return response
    """

    def __init__(
            self,
            retrieval_service: RetrievalService,
            generation_service: GenerationService,
            citation_service: CitationService,
    ):
        self.retrieval_service = retrieval_service
        self.generation_service = generation_service
        self.citation_service = citation_service

    def answer_query(
            self,
            query: str,
            top_k: int,
            max_context_chunks: int,
            min_score_threshold: float | None = None,
            include_debug: bool = False,
    ) -> QueryResponse:
        request_id = str(uuid.uuid4())

        total_start = time.perf_counter()

        retrieval_start = time.perf_counter()
        retrieved = self.retrieval_service.retrieve(
            query=query,
            top_k=top_k,
        )
        retrieval_latency_ms = (time.perf_counter() - retrieval_start) * 1000

        # Apply optional score threshold
        if min_score_threshold is not None:
            retrieved = [r for r in retrieved if r.score >= min_score_threshold]

        context_chunks = retrieved[:max_context_chunks]

        generation_start = time.perf_counter()

        fallback_triggered = len(context_chunks) == 0

        if fallback_triggered:
            answer = self.generation_service.fallback_answer()
            citations = []
        else:
            answer = self.generation_service.generate_answer(
                query=query,
                context_chunks=context_chunks,
            )
            citations = self.citation_service.build_citations(context_chunks)

        generation_latency_ms = (time.perf_counter() - generation_start) * 1000
        total_latency_ms = (time.perf_counter() - total_start) * 1000

        debug = None
        if include_debug:
            debug = {
                "retrieved_chunks": [
                    {
                        "document_title": chunk.document_title,
                        "source_path": chunk.source_path,
                        "chunk_index": chunk.chunk_index,
                        "score": round(chunk.score, 4),
                        "content_preview": chunk.content[:300],
                    }
                    for chunk in retrieved
                ],
                "context_chunk_count": len(context_chunks),
            }

        return QueryResponse(
            answer=answer,
            citations=citations,
            request_id=request_id,
            fallback_triggered=fallback_triggered,
            latency_ms={
                "retrieval": round(retrieval_latency_ms, 2),
                "generation": round(generation_latency_ms, 2),
                "total": round(total_latency_ms, 2),
            },
            debug=debug,
        )
