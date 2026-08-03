import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.db import dispose_engine
from app.services.vector_store import VectorStoreService
from app.graphs.workflow import build_qa_planner_graph

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for FastAPI.
    """
    logger.info("Starting up Agentic QA Planner backend...")
    
    # Initialize global AI dependencies
    vector_service = VectorStoreService()
    qa_graph = build_qa_planner_graph(vector_service)
    
    app.state.vector_service = vector_service
    app.state.qa_graph = qa_graph
    
    yield
    
    logger.info("Shutting down Agentic QA Planner backend...")
    await dispose_engine()


app = FastAPI(
    title=settings.APP_NAME,
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

# Set up CORS middleware
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include the v1 API router
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
