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
from app.services.reranking_service import RerankingService
from app.services.retrieval_service import RetrievalService, RetrievedChunk


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
            reranking_service: RerankingService | None = None,
    ):
        self.retrieval_service = retrieval_service
        self.generation_service = generation_service
        self.citation_service = citation_service
        self.metrics_service = metrics_service
        self.cache_service = cache_service
        self.reranking_service = reranking_service
        self.logger = get_logger(__name__)

    def answer_query(
            self,
            query: str,
            top_k: int,
            max_context_chunks: int,
            min_score_threshold: float | None = None,
            include_debug: bool = False,
            use_cache: bool = True,
            use_reranker: bool = False,
            reranker_candidate_pool: int = 8,
    ) -> QueryResponse:
        request_id = str(uuid.uuid4())
        normalized_query = self._normalize_query(query)

        effective_top_k = max(top_k, reranker_candidate_pool if use_reranker else top_k)

        cache_key = self._build_cache_key(
            normalized_query=normalized_query,
            top_k=effective_top_k,
            max_context_chunks=max_context_chunks,
            min_score_threshold=min_score_threshold,
            use_reranker=use_reranker,
            reranker_candidate_pool=reranker_candidate_pool
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
                    use_reranker=use_reranker,
                    reranker_candidate_pool=reranker_candidate_pool,
                )

                # Persist lightweight query log even for cache hit
                self.metrics_service.persist_query_log(
                    request_id=request_id,
                    query_text=query,
                    top_k=effective_top_k,
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
            top_k=effective_top_k,
        )
        retrieval_latency_ms = (time.perf_counter() - retrieval_start) * 1000

        filtered = retrieved
        # Apply optional score threshold
        if min_score_threshold is not None:
            filtered = [r for r in retrieved if r.score >= min_score_threshold]

        reranked = filtered
        reranker_applied = False

        if use_reranker and self.reranking_service is not None and filtered:
            reranked = self.reranking_service.rerank(
                query=query,
                chunks=filtered,
            )
            reranker_applied = True

        context_chunks = reranked[:max_context_chunks]

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
                "reranker_applied": reranker_applied,
                "retrieved_chunks": self.get_retrieved_chunks(retrieved),
                "filtered_chunks": self.get_retrieved_chunks(filtered),
                "reranked_chunks": self.get_retrieved_chunks(reranked),
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
            effective_top_k=effective_top_k,
            max_context_chunks=max_context_chunks,
            min_score_threshold=min_score_threshold,
            use_reranker=use_reranker,
            reranker_applied=reranker_applied,
            retrieved_count=len(retrieved),
            filtered_count=len(filtered),
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
            top_k=effective_top_k,
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

    @staticmethod
    def get_retrieved_chunks(retrieved: list[RetrievedChunk]) -> list[dict]:
        return [
            {
                "document_title": chunk.document_title,
                "source_path": chunk.source_path,
                "chunk_index": chunk.chunk_index,
                "score": round(chunk.score, 4),
                "content_preview": chunk.content[:300],
            }
            for chunk in retrieved
        ]

    def _normalize_query(self, query: str) -> str:
        return " ".join(query.strip().lower().split())

    def _build_cache_key(
            self,
            normalized_query: str,
            top_k: int,
            max_context_chunks: int,
            min_score_threshold: float | None,
            use_reranker: bool,
            reranker_candidate_pool: int
    ) -> str:
        raw = f"{normalized_query}|{top_k}|{max_context_chunks}|{min_score_threshold}|{use_reranker}|{reranker_candidate_pool}"
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
