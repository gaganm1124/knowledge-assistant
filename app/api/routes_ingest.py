from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain.schemas import IngestRequest, IngestResponse

router = APIRouter(prefix="/v1/documents", tags=["documents"])


@router.post("/ingest", response_model=IngestResponse)
def ingest_documents(
    request: IngestRequest,
    db: Session = Depends(get_db),
) -> IngestResponse:
    # Week 1 stub
    # Week 2: implement parsing + chunking + DB persistence
    return IngestResponse(
        documents_ingested=0,
        chunks_created=0,
        skipped_documents=0,
        status=f"stub: ingest endpoint ready for source_dir={request.source_dir}",
    )