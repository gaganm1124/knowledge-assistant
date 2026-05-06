from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain.schemas import RetrievalDebugRequest
from app.providers.embeddings.factory import get_embedding_provider
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import RetrievalService

router = APIRouter(prefix="/v1/retrieval", tags=["debug"])


@router.post("/debug")
def retrieval_debug(request: RetrievalDebugRequest, db: Session = Depends(get_db)) -> dict:
    # Week 3: implement actual vector retrieval debug

    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty.")

    embedding_provider = get_embedding_provider()
    embedding_service = EmbeddingService(provider=embedding_provider)

    retrieval_service = RetrievalService(
        db=db,
        embedding_service=embedding_service,
    )
    results = retrieval_service.retrieve(
        query=request.query,
        top_k=request.top_k,
    )

    return {
        "status": "success",
        "query": request.query,
        "top_k": request.top_k,
        "results": [
            {
                "document_title": r.document_title,
                "source_path": r.source_path,
                "chunk_index": r.chunk_index,
                "section_heading": r.section_heading,
                "score": round(r.score, 4),
                "content_preview": r.content[:300],
            }
            for r in results
        ],
    }
