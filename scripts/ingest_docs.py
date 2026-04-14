from app.db.session import SessionLocal
from app.services.chunking_service import ChunkingService
from app.services.document_parser import DocumentParser
from app.services.ingestion_service import IngestionService
from app.core.config import settings


def main():
    db = SessionLocal()
    try:
        parser = DocumentParser()
        chunker = ChunkingService(
            chunk_size=settings.default_chunk_size,
            chunk_overlap=settings.default_chunk_overlap,
        )
        service = IngestionService(db=db, parser=parser, chunker=chunker)

        result = service.ingest_directory(
            source_dir="data/raw",
            recursive=True,
            file_types=["md", "txt"],
        )

        print("Ingestion complete:")
        print(f"  documents_ingested = {result.documents_ingested}")
        print(f"  chunks_created     = {result.chunks_created}")
        print(f"  skipped_documents  = {result.skipped_documents}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
