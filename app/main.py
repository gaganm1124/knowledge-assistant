from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.api.routes_debug import router as debug_router
from app.api.routes_health import router as health_router
from app.api.routes_ingest import router as ingest_router
from app.api.routes_query import router as query_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()

    # Ensure pgvector is available before creating tables that use VECTOR columns.
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

        # Create tables on startup (good for Week 1).
        # In later weeks, you can switch to Alembic migrations.
        Base.metadata.create_all(bind=connection)

    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(ingest_router)
app.include_router(query_router)
app.include_router(debug_router)
