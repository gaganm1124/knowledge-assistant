import uuid

from fastapi import APIRouter
from app.domain.schemas import QueryRequest, QueryResponse

router = APIRouter(prefix="/v1", tags=["query"])


@router.post("/query", response_model=QueryResponse)
def query_knowledge_base(request: QueryRequest) -> QueryResponse:
    # Week 1 stub
    # Week 3-4: implement retrieval + generation
    request_id = str(uuid.uuid4())

    return QueryResponse(
        answer="Stub response: query endpoint is wired. Retrieval/generation will be added in Week 3-4.",
        citations=[],
        request_id=request_id,
        fallback_triggered=True,
        latency_ms={
            "retrieval": 0.0,
            "generation": 0.0,
            "total": 0.0,
        },
        debug={"received_query": request.query} if request.include_debug else None,
    )