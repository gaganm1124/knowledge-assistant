# Knowledge Assistant

Production-style RAG API for querying internal engineering documentation (RFCs, runbooks, API docs, postmortems).

## Week 1 Scope
- FastAPI service skeleton
- Dockerized Postgres + pgvector
- SQLAlchemy models for documents and chunks
- Route stubs for ingest, query, and retrieval debug

## Planned Features
- Document ingestion
- Chunking with metadata preservation
- Embeddings + pgvector retrieval
- Grounded answer generation with citations
- Latency instrumentation
- Evaluation scripts

## Run Locally

```bash
cp .env.template .env
docker-compose up --build