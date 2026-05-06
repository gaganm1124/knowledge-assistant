from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Chunk, Document
from app.services.embedding_service import EmbeddingService


@dataclass
class RetrievedChunk:
    chunk_id: str
    document_id: str
    document_title: str
    source_path: str
    chunk_index: int
    section_heading: str | None
    content: str
    score: float


class RetrievalService:
    """
    Week 3 retrieval:
    - embeds query
    - searches top-k nearest chunks using pgvector cosine distance
    - returns chunk content + metadata
    """

    def __init__(
            self,
            db: Session,
            embedding_service: EmbeddingService,
    ):
        self.db = db
        self.embedding_service = embedding_service

    def retrieve(
            self,
            query: str,
            top_k: int = 5,
    ) -> list[RetrievedChunk]:
        query_embedding = self.embedding_service.embed_text(query)

        # cosine_distance: lower is better
        distance_expr = Chunk.embedding.cosine_distance(query_embedding)

        stmt = (
            select(
                Chunk,
                Document,
                distance_expr.label("distance"),
            )
            .join(Document, Chunk.document_id == Document.id)
            .where(Chunk.embedding.is_not(None))
            .order_by(distance_expr.asc())
            .limit(top_k)
        )

        rows = self.db.execute(stmt).all()

        results: list[RetrievedChunk] = []

        for chunk, document, distance in rows:
            # Convert distance to a more intuitive "score" where higher is better
            # score ~= 1 - distance (not perfect, but easy to interpret for debugging)
            score = 1.0 - float(distance)

            results.append(
                RetrievedChunk(
                    chunk_id=str(chunk.id),
                    document_id=str(document.id),
                    document_title=document.title,
                    source_path=document.source_path,
                    chunk_index=chunk.chunk_index,
                    section_heading=chunk.section_heading,
                    content=chunk.content,
                    score=score,
                )
            )

        return results
