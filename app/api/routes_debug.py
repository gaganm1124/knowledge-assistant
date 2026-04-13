from fastapi import APIRouter

from app.domain.schemas import RetrievalDebugRequest

router = APIRouter(prefix="/v1/retrieval", tags=["debug"])


@router.post("/debug")
def retrieval_debug(request: RetrievalDebugRequest) -> dict:
    # Week 3: implement actual vector retrieval debug
    return {
        "status": "stub",
        "message": "Retrieval debug endpoint is ready. Actual vector search will be added in Week 3.",
        "query": request.query,
        "top_k": request.top_k,
        "results": [],
    }