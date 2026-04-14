from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.domain.schemas import IngestRequest, IngestResponse
from app.services.chunking_service import ChunkingService
from app.services.document_parser import DocumentParser
from app.services.ingestion_service import IngestionService

router = APIRouter(prefix="/v1/documents", tags=["documents"])


@router.post("/ingest", response_model=IngestResponse)
def ingest_documents(
        request: IngestRequest,
        db: Session = Depends(get_db),
) -> IngestResponse:
    if request.chunking_strategy != "fixed":
        raise HTTPException(
            status_code=400,
            detail="Only 'fixed' chunking_strategy is supported in Week 2.",
        )

    parser = DocumentParser()
    chunker = ChunkingService(
        chunk_size=settings.default_chunk_size,
        chunk_overlap=settings.default_chunk_overlap,
    )
    ingestion_service = IngestionService(
        db=db,
        parser=parser,
        chunker=chunker,
    )

    result = ingestion_service.ingest_directory(
        source_dir=request.source_dir or "data/raw",
        recursive=request.recursive,
        file_types=request.file_types,
    )

    return IngestResponse(
        documents_ingested=result.documents_ingested,
        chunks_created=result.chunks_created,
        skipped_documents=result.skipped_documents,
        status="success",
    )
