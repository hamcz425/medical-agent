import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = "Medical RAG Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite+aiosqlite:///./medical_agent.db"

    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    HUGGINGFACE_TOKEN: str = ""
    HUGGINGFACE_MODEL: str = "Qwen/Qwen2.5-7B-Instruct"
    HUGGINGFACE_EMBEDDING_MODEL: str = "BAAI/bge-m3"
    USE_LOCAL_EMBEDDING: bool = True
    HUGGINGFACE_API_URL: str = "https://api-inference.huggingface.co/v1"

    ZHIPUAI_API_KEY: str = ""
    ZHIPUAI_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4/"
    ZHIPUAI_MODEL: str = "glm-4-flash"

    CHROMA_PERSIST_DIR: str = "./chroma_db"

    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080"]

    def __init__(self):
        self.APP_NAME = os.getenv("APP_NAME", self.APP_NAME)
        self.APP_VERSION = os.getenv("APP_VERSION", self.APP_VERSION)
        self.DEBUG = os.getenv("DEBUG", "true").lower() == "true"
        self.DATABASE_URL = os.getenv("DATABASE_URL", self.DATABASE_URL)
        self.SECRET_KEY = os.getenv("SECRET_KEY", self.SECRET_KEY)
        self.ALGORITHM = os.getenv("ALGORITHM", self.ALGORITHM)
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
        self.HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", self.HUGGINGFACE_TOKEN)
        self.HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL", self.HUGGINGFACE_MODEL)
        self.HUGGINGFACE_EMBEDDING_MODEL = os.getenv("HUGGINGFACE_EMBEDDING_MODEL", self.HUGGINGFACE_EMBEDDING_MODEL)
        self.USE_LOCAL_EMBEDDING = os.getenv("USE_LOCAL_EMBEDDING", "true").lower() == "true"
        self.HUGGINGFACE_API_URL = os.getenv("HUGGINGFACE_API_URL", self.HUGGINGFACE_API_URL)
        self.ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY", self.ZHIPUAI_API_KEY)
        self.ZHIPUAI_BASE_URL = os.getenv("ZHIPUAI_BASE_URL", self.ZHIPUAI_BASE_URL)
        self.ZHIPUAI_MODEL = os.getenv("ZHIPUAI_MODEL", self.ZHIPUAI_MODEL)
        self.CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", self.CHROMA_PERSIST_DIR)
        origins = os.getenv("ALLOWED_ORIGINS", "")
        self.ALLOWED_ORIGINS = [o.strip() for o in origins.split(",") if o.strip()] if origins else ["http://localhost:3000", "http://localhost:3001", "http://localhost:8080"]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
