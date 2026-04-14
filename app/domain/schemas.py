from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    app_name: str
    db_status: str


class IngestRequest(BaseModel):
    source_dir: str | None = Field(default="data/raw")
    recursive: bool = True
    file_types: list[str] = Field(default_factory=lambda: ["md", "txt"])
    chunking_strategy: str = "fixed"


class IngestResponse(BaseModel):
    documents_ingested: int
    chunks_created: int
    skipped_documents: int
    status: str


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    max_context_chunks: int = 4
    min_score_threshold: float | None = None
    use_reranker: bool = False
    include_debug: bool = False
    use_cache: bool = True


class Citation(BaseModel):
    document_title: str
    chunk_index: int
    section_heading: str | None = None


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
    request_id: str
    fallback_triggered: bool
    latency_ms: dict[str, float]
    debug: dict | None = None


class RetrievalDebugRequest(BaseModel):
    query: str
    top_k: int = 5
