from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.domain.schemas import QueryRequest, QueryResponse
from app.providers.embeddings.factory import get_embedding_provider, get_llm_provider, get_reranking_provider
from app.services.citation_service import CitationService
from app.services.embedding_service import EmbeddingService
from app.services.generation_service import GenerationService
from app.services.metrics_service import MetricsService
from app.services.query_service import QueryService
from app.services.reranking_service import RerankingService
from app.services.retrieval_service import RetrievalService
from app.services.runtime_state import query_cache

router = APIRouter(prefix="/v1", tags=["query"])


@router.post("/query", response_model=QueryResponse)
def query_knowledge_base(request: QueryRequest, db: Session = Depends(get_db)) -> QueryResponse:
    # Week 1 stub
    # Week 3-4: implement retrieval + generation
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty.")

    # Week 4: reranker/cache flags are accepted by schema but not implemented yet.
    embedding_provider = get_embedding_provider()
    embedding_service = EmbeddingService(provider=embedding_provider)

    retrieval_service = RetrievalService(
        db=db,
        embedding_service=embedding_service,
    )

    llm_provider = get_llm_provider()
    generation_service = GenerationService(llm_provider=llm_provider)

    citation_service = CitationService()

    metrics_service = MetricsService(db=db)
    cache_service = query_cache if settings.enable_cache else None

    reranking_provider = get_reranking_provider()
    reranking_service = RerankingService(provider=reranking_provider) if settings.enable_reranker else None

    query_service = QueryService(
        retrieval_service=retrieval_service,
        generation_service=generation_service,
        citation_service=citation_service,
        metrics_service=metrics_service,
        cache_service=cache_service,
        reranking_service=reranking_service,
    )

    return query_service.answer_query(
        query=request.query,
        top_k=request.top_k,
        max_context_chunks=request.max_context_chunks,
        min_score_threshold=request.min_score_threshold,
        include_debug=request.include_debug,
        use_cache=request.use_cache,
        use_reranker=request.use_reranker,
        reranker_candidate_pool=settings.reranker_candidate_pool,
    )
