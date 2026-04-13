# Architecture Overview: Knowledge Assistant

## Purpose
The Knowledge Assistant ingests internal documentation, runbooks, and postmortems,
and surfaces relevant context through a semantic search API.

## Components

### Ingestion Pipeline
- Watches `data/raw/` for new or updated markdown files
- Chunks documents into ~512-token segments
- Generates embeddings via the configured embedding model
- Stores embeddings and metadata in pgvector

### API Layer
- FastAPI application exposing `/search` and `/ingest` endpoints
- `/search` accepts a natural language query and returns top-k relevant chunks
- `/ingest` triggers manual re-ingestion of a specified file

### Storage
- **PostgreSQL + pgvector**: stores document chunks and their vector embeddings
- **Raw file store**: `data/raw/` directory, version-controlled markdown files

### Retrieval
- Cosine similarity search over pgvector
- Results include source document, chunk text, and similarity score

## Data Flow
```
Markdown file → chunker → embedder → pgvector
User query    → embedder → pgvector (ANN search) → ranked results → API response
```

## Key Design Decisions
- Markdown chosen as source format for human editability and git diff-friendliness
- Chunk size of 512 tokens balances retrieval precision against context coverage
- pgvector preferred over a dedicated vector DB to reduce operational complexity