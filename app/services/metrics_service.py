from __future__ import annotations

from app.db.models import QueryLog


class MetricsService:
    """
    Persists request-level query telemetry into query_logs.
    """

    def __init__(self, db):
        self.db = db

    def persist_query_log(
            self,
            request_id: str,
            query_text: str,
            top_k: int,
            max_context_chunks: int,
            retrieved_doc_ids: list[str],
            retrieved_chunk_ids: list[str],
            retrieval_latency_ms: float,
            generation_latency_ms: float,
            total_latency_ms: float,
            cache_hit: bool,
            fallback_triggered: bool,
    ) -> None:
        row = QueryLog(
            request_id=request_id,
            query_text=query_text,
            top_k=top_k,
            max_context_chunks=max_context_chunks,
            retrieved_doc_ids=retrieved_doc_ids,
            retrieved_chunk_ids=retrieved_chunk_ids,
            retrieval_latency_ms=retrieval_latency_ms,
            generation_latency_ms=generation_latency_ms,
            total_latency_ms=total_latency_ms,
            cache_hit=cache_hit,
            fallback_triggered=fallback_triggered,
        )

        self.db.add(row)
        self.db.commit()
