import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import init_db
from app.routers import auth, documents, rag, system

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("Database tables created.")

    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.isdir(static_dir) and os.path.exists(os.path.join(static_dir, "index.html")):
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

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir) and os.path.exists(os.path.join(static_dir, "index.html")):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
    logger.info("Serving frontend from %s", static_dir)


@app.get("/api")
async def api_root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }
