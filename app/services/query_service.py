from __future__ import annotations

import hashlib
import time
import uuid

from app.core.logging import get_logger, log_event
from app.domain.schemas import QueryResponse
from app.services.cache_service import CacheService
from app.services.citation_service import CitationService
from app.services.generation_service import GenerationService
from app.services.metrics_service import MetricsService
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
            metrics_service: MetricsService,
            cache_service: CacheService | None = None,
    ):
        self.retrieval_service = retrieval_service
        self.generation_service = generation_service
        self.citation_service = citation_service
        self.metrics_service = metrics_service
        self.cache_service = cache_service
        self.logger = get_logger(__name__)

    def answer_query(
            self,
            query: str,
            top_k: int,
            max_context_chunks: int,
            min_score_threshold: float | None = None,
            include_debug: bool = False,
            use_cache: bool = True,
    ) -> QueryResponse:
        request_id = str(uuid.uuid4())
        normalized_query = self._normalize_query(query)
        cache_key = self._build_cache_key(
            normalized_query=normalized_query,
            top_k=top_k,
            max_context_chunks=max_context_chunks,
            min_score_threshold=min_score_threshold,
        )

        total_start = time.perf_counter()

        if use_cache and self.cache_service is not None:
            cached = self.cache_service.get(cache_key)
            if cached is not None:
                cached.request_id = request_id  # fresh request ID for this response
                cached.debug = self._merge_debug(
                    cached.debug,
                    {
                        "cache_hit": True,
                        "cache_key": cache_key if include_debug else None,
                    } if include_debug else None,
                )

                log_event(
                    self.logger,
                    "query_cache_hit",
                    request_id=request_id,
                    query=normalized_query,
                    top_k=top_k,
                    max_context_chunks=max_context_chunks,
                )

                # Persist lightweight query log even for cache hit
                self.metrics_service.persist_query_log(
                    request_id=request_id,
                    query_text=query,
                    top_k=top_k,
                    max_context_chunks=max_context_chunks,
                    retrieved_doc_ids=[],
                    retrieved_chunk_ids=[],
                    retrieval_latency_ms=0.0,
                    generation_latency_ms=0.0,
                    total_latency_ms=(time.perf_counter() - total_start) * 1000,
                    cache_hit=True,
                    fallback_triggered=cached.fallback_triggered,
                )

                return cached

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
                "cache_hit": False,
                "cache_key": cache_key,
                "normalized_query": normalized_query,
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

        response = QueryResponse(
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

        log_event(
            self.logger,
            "query_completed",
            request_id=request_id,
            query=normalized_query,
            top_k=top_k,
            max_context_chunks=max_context_chunks,
            min_score_threshold=min_score_threshold,
            retrieved_count=len(retrieved),
            context_count=len(context_chunks),
            cache_hit=False,
            fallback_triggered=fallback_triggered,
            retrieval_latency_ms=round(retrieval_latency_ms, 2),
            generation_latency_ms=round(generation_latency_ms, 2),
            total_latency_ms=round(total_latency_ms, 2),
        )

        self.metrics_service.persist_query_log(
            request_id=request_id,
            query_text=query,
            top_k=top_k,
            max_context_chunks=max_context_chunks,
            retrieved_doc_ids=list({r.document_id for r in retrieved}),
            retrieved_chunk_ids=[r.chunk_id for r in retrieved],
            retrieval_latency_ms=round(retrieval_latency_ms, 2),
            generation_latency_ms=round(generation_latency_ms, 2),
            total_latency_ms=round(total_latency_ms, 2),
            cache_hit=False,
            fallback_triggered=fallback_triggered,
        )

        if use_cache and self.cache_service is not None:
            self.cache_service.set(cache_key, response)

        return response

    def _normalize_query(self, query: str) -> str:
        return " ".join(query.strip().lower().split())

    def _build_cache_key(
            self,
            normalized_query: str,
            top_k: int,
            max_context_chunks: int,
            min_score_threshold: float | None,
    ) -> str:
        raw = f"{normalized_query}|{top_k}|{max_context_chunks}|{min_score_threshold}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _merge_debug(self, existing: dict | None, extra: dict | None) -> dict | None:
        if existing is None and extra is None:
            return None
        if existing is None:
            return extra
        if extra is None:
            return existing

        merged = dict(existing)
        for k, v in extra.items():
            if v is not None:
                merged[k] = v
        return merged
