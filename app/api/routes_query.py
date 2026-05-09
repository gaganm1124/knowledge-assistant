import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain.schemas import QueryRequest, QueryResponse
from app.providers.embeddings.local_provider import LocalEmbeddingProvider
from app.providers.llm.local_provider import LocalLLMProvider
from app.services.citation_service import CitationService
from app.services.embedding_service import EmbeddingService
from app.services.generation_service import GenerationService
from app.services.query_service import QueryService
from app.services.retrieval_service import RetrievalService

router = APIRouter(prefix="/v1", tags=["query"])


@router.post("/query", response_model=QueryResponse)
def query_knowledge_base(request: QueryRequest, db: Session = Depends(get_db)) -> QueryResponse:
    # Week 1 stub
    # Week 3-4: implement retrieval + generation
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty.")

    # Week 4: reranker/cache flags are accepted by schema but not implemented yet.
    embedding_provider = LocalEmbeddingProvider()
    embedding_service = EmbeddingService(provider=embedding_provider)

    retrieval_service = RetrievalService(
        db=db,
        embedding_service=embedding_service,
    )

    llm_provider = LocalLLMProvider()
    generation_service = GenerationService(llm_provider=llm_provider)

    citation_service = CitationService()

    query_service = QueryService(
        retrieval_service=retrieval_service,
        generation_service=generation_service,
        citation_service=citation_service,
    )

    return query_service.answer_query(
        query=request.query,
        top_k=request.top_k,
        max_context_chunks=request.max_context_chunks,
        min_score_threshold=request.min_score_threshold,
        include_debug=request.include_debug,
    )
