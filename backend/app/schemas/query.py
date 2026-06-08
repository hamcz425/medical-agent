from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)
    retrieval_mode: str = Field(default="hybrid", pattern="^(vector|bm25|hybrid)$")


class SourceDocument(BaseModel):
    id: int
    title: str
    category: str
    source: Optional[str]
    content_preview: str
    rrf_score: Optional[float] = None
    vector_score: Optional[float] = None
    bm25_score: Optional[float] = None


class VerificationResult(BaseModel):
    passed: bool
    reason: str


class QueryResponse(BaseModel):
    id: int
    query: str
    response: str
    confidence: float
    processing_time: int
    sources: list[SourceDocument]
    retrieval_mode: str = "hybrid"
    verification: Optional[VerificationResult] = None
    created_at: datetime


class QueryHistoryResponse(BaseModel):
    queries: list[QueryResponse]
    total: int


class FeedbackRequest(BaseModel):
    query_log_id: int
    rating: str = Field(..., pattern="^(correct|incorrect|partial)$")
    comment: Optional[str] = Field(None, max_length=2000)
    corrected_response: Optional[str] = Field(None, max_length=5000)


class FeedbackResponse(BaseModel):
    success: bool
    message: str


class SystemStats(BaseModel):
    total_documents: int
    processed_documents: int
    indexed_documents: int
    total_queries: int
    average_response_time: float
    system_health: str
    document_categories: dict[str, int]
    recent_queries: list[QueryResponse]
