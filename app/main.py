from contextlib import asynccontextmanager

import uvicorn

from fastapi import FastAPI

from app.api.routes_debug import router as debug_router
from app.api.routes_health import router as health_router
from app.api.routes_ingest import router as ingest_router
from app.api.routes_query import router as query_router
from app.core.config import settings
from app.core.logging import configure_logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
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

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.app_host, port=settings.app_port, reload=settings.debug)
