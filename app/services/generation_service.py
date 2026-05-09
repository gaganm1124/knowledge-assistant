from __future__ import annotations

from app.providers.llm.base import LLMProvider
from app.services.retrieval_service import RetrievedChunk


class GenerationService:
    """
    Week 4 generation:
    - builds a grounded prompt from retrieved chunks
    - instructs the model to answer only from context
    - supports fallback if context is insufficient
    """

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def generate_answer(
            self,
            query: str,
            context_chunks: list[RetrievedChunk],
    ) -> str:
        if not context_chunks:
            return self.fallback_answer()

        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(query=query, context_chunks=context_chunks)

        return self.llm_provider.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

    def fallback_answer(self) -> str:
        return (
            "I don’t have enough evidence from the indexed documents to answer that confidently. "
            "Please try rephrasing the question or ingest additional relevant documentation."
        )

    def _build_system_prompt(self) -> str:
        return (
            "You are an internal engineering documentation assistant.\n"
            "Answer the user's question using ONLY the provided context.\n"
            "If the context does not contain enough information, say that you do not have enough evidence.\n"
            "Do NOT invent details.\n"
            "Be concise, accurate, and practical.\n"
        )

    def _build_user_prompt(
            self,
            query: str,
            context_chunks: list[RetrievedChunk],
    ) -> str:
        context_blocks = []

        for idx, chunk in enumerate(context_chunks, start=1):
            heading = f" | section: {chunk.section_heading}" if chunk.section_heading else ""
            context_blocks.append(
                f"[Source {idx}] doc: {chunk.document_title}{heading}\n"
                f"{chunk.content}"
            )

        context_text = "\n\n".join(context_blocks)

        return (
            f"User question:\n{query}\n\n"
            f"Context:\n{context_text}\n\n"
            "Instructions:\n"
            "- Answer using only the provided context.\n"
            "- If the answer is not fully supported, say so clearly.\n"
            "- Do not fabricate steps, commands, or policies.\n"
        )
