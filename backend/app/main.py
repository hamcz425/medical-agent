import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.config import get_settings
from app.database import init_db
from app.routers import auth, documents, rag, system

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
INDEX_HTML = os.path.join(STATIC_DIR, "index.html") if STATIC_DIR else None


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("Database tables created.")

    if INDEX_HTML and os.path.exists(INDEX_HTML):
        from app.startup import seed_database
        await seed_database()

    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="企业级医疗RAG智能问答系统",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(rag.router)
app.include_router(system.router)


@app.get("/api")
async def api_root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


if INDEX_HTML and os.path.exists(INDEX_HTML):
    @app.get("/{full_path:path}")
    async def serve_frontend(request: Request, full_path: str):
        static_file = os.path.join(STATIC_DIR, full_path)
        if full_path and os.path.isfile(static_file):
            return FileResponse(static_file)
        return FileResponse(INDEX_HTML)
