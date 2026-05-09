from __future__ import annotations

from app.domain.schemas import Citation
from app.services.retrieval_service import RetrievedChunk


class CitationService:
    """
    Converts retrieved chunks into API citation objects.
    Week 4 keeps it simple: one citation per retrieved chunk in context.
    """

    def build_citations(
            self,
            retrieved_chunks: list[RetrievedChunk],
    ) -> list[Citation]:
        citations: list[Citation] = []

        for chunk in retrieved_chunks:
            citations.append(
                Citation(
                    document_title=chunk.document_title,
                    chunk_index=chunk.chunk_index,
                    section_heading=chunk.section_heading,
                )
            )

        return citations
