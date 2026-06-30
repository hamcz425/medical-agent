import os
import secrets
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = "Medical RAG Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: str = "sqlite+aiosqlite:///./medical_agent.db"

    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    ZHIPUAI_API_KEY: str = ""
    ZHIPUAI_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4/"
    ZHIPUAI_MODEL: str = "glm-4-flash"

    CHROMA_PERSIST_DIR: str = "./chroma_db"

    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:8080"]
    SEED_DEMO_DATA: bool = False

    def __init__(self):
        self.APP_NAME = os.getenv("APP_NAME", self.APP_NAME)
        self.APP_VERSION = os.getenv("APP_VERSION", self.APP_VERSION)
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        self.DATABASE_URL = os.getenv("DATABASE_URL", self.DATABASE_URL)
        self.SECRET_KEY = os.getenv("SECRET_KEY", "")
        self.ALGORITHM = os.getenv("ALGORITHM", self.ALGORITHM)
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
        self.ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY", self.ZHIPUAI_API_KEY)
        self.ZHIPUAI_BASE_URL = os.getenv("ZHIPUAI_BASE_URL", self.ZHIPUAI_BASE_URL)
        self.ZHIPUAI_MODEL = os.getenv("ZHIPUAI_MODEL", self.ZHIPUAI_MODEL)
        self.CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", self.CHROMA_PERSIST_DIR)
        self.SEED_DEMO_DATA = os.getenv("SEED_DEMO_DATA", "false").lower() == "true"

        origins = os.getenv("ALLOWED_ORIGINS", "")
        if origins:
            self.ALLOWED_ORIGINS = [o.strip() for o in origins.split(",") if o.strip()]
        elif self.DEBUG:
            self.ALLOWED_ORIGINS = ["*"]
        else:
            self.ALLOWED_ORIGINS = ["http://localhost:3000", "http://localhost:3001"]

    def validate(self):
        errors = []
        if not self.SECRET_KEY:
            errors.append("SECRET_KEY is required. Set it in environment variables.")
        if not self.ZHIPUAI_API_KEY:
            errors.append("ZHIPUAI_API_KEY is required. Set it in environment variables.")
        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(errors))


@lru_cache()
def get_settings() -> Settings:
    return Settings()
