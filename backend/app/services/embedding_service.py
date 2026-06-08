import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

import sys
sys.stdout.reconfigure(encoding='utf-8')

from sentence_transformers import SentenceTransformer
from app.config import get_settings

settings = get_settings()

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
print(f"Loading embedding model: {MODEL_NAME} ...")
_model = SentenceTransformer(MODEL_NAME)
print("Embedding model loaded.")


class EmbeddingService:
    def __init__(self):
        self._model = _model

    def initialize(self):
        pass

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        embeddings = self._model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return embeddings.tolist()

    def embed_texts_sync(self, texts: list[str]) -> list[list[float]]:
        return self.embed_texts(texts)

    def embed_query(self, query: str) -> list[float]:
        return self.embed_texts([query])[0]

    @property
    def dimension(self) -> int:
        return 384


embedding_service = EmbeddingService()
