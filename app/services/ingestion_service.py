from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Chunk, Document
from app.services.chunking_service import ChunkingService
from app.services.document_parser import DocumentParser
from app.utils.file_utils import compute_sha256, discover_files


@dataclass
class IngestionResult:
    documents_ingested: int
    chunks_created: int
    skipped_documents: int


class IngestionService:
    """
    Week 2 ingestion pipeline:
    1. Discover files
    2. Parse documents
    3. Skip if source_path already exists
    4. Chunk normalized text
    5. Persist Document + Chunk rows
    """

    def __init__(
            self,
            db: Session,
            parser: DocumentParser,
            chunker: ChunkingService,
    ):
        self.db = db
        self.parser = parser
        self.chunker = chunker

    def ingest_directory(
            self,
            source_dir: str,
            recursive: bool = True,
            file_types: list[str] | None = None,
    ) -> IngestionResult:
        files = discover_files(
            source_dir=source_dir,
            recursive=recursive,
            file_types=file_types,
        )

        documents_ingested = 0
        chunks_created = 0
        skipped_documents = 0

        for file_path in files:
            if self._document_exists_by_path(str(file_path)):
                skipped_documents += 1
                continue

            parsed = self.parser.parse(file_path)
            checksum = compute_sha256(parsed.normalized_text)

            document = Document(
                title=parsed.title,
                source_path=parsed.source_path,
                doc_type=parsed.doc_type,
                checksum=checksum,
            )

            self.db.add(document)
            self.db.flush()  # ensures document.id is available

            chunk_payloads = self.chunker.chunk_text(parsed.normalized_text)

            for payload in chunk_payloads:
                chunk = Chunk(
                    document_id=document.id,
                    chunk_index=payload.chunk_index,
                    section_heading=payload.section_heading,
                    content=payload.content,
                    token_estimate=payload.token_estimate,
                    char_start=payload.char_start,
                    char_end=payload.char_end,
                    # Week 2: embeddings not yet added
                    embedding=None,
                )
                self.db.add(chunk)

            documents_ingested += 1
            chunks_created += len(chunk_payloads)

        self.db.commit()

        return IngestionResult(
            documents_ingested=documents_ingested,
            chunks_created=chunks_created,
            skipped_documents=skipped_documents,
        )

    def _document_exists_by_path(self, source_path: str) -> bool:
        stmt = select(Document.id).where(Document.source_path == source_path)
        return self.db.execute(stmt).scalar_one_or_none() is not None
