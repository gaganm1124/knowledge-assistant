from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ChunkPayload:
    chunk_index: int
    content: str
    section_heading: str | None
    char_start: int
    char_end: int
    token_estimate: int | None


class ChunkingService:
    """
    Week 2 chunker:
    - fixed-size character chunks
    - overlap between chunks
    - simple token estimate
    """

    def __init__(self, chunk_size: int = 700, chunk_overlap: int = 120):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> list[ChunkPayload]:
        if not text.strip():
            return []

        chunks: list[ChunkPayload] = []

        start = 0
        chunk_index = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    ChunkPayload(
                        chunk_index=chunk_index,
                        content=chunk_text,
                        section_heading=None,  # Week 2: not extracting headings yet
                        char_start=start,
                        char_end=end,
                        token_estimate=self._estimate_tokens(chunk_text),
                    )
                )
                chunk_index += 1

            if end >= text_length:
                break

            start = max(0, end - self.chunk_overlap)

        return chunks

    def _estimate_tokens(self, text: str) -> int:
        # rough heuristic; good enough for Week 2
        return max(1, len(text) // 4)
