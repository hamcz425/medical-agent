from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    category: str = Field(..., pattern="^(medical_record|research_paper|drug_info|clinical_guide)$")
    source: Optional[str] = None
    metadata_json: dict = Field(default_factory=dict)


class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, pattern="^(medical_record|research_paper|drug_info|clinical_guide)$")
    source: Optional[str] = None
    metadata_json: Optional[dict] = None


class DocumentResponse(BaseModel):
    id: int
    title: str
    content: str
    category: str
    source: Optional[str]
    file_type: Optional[str]
    file_size: Optional[int]
    status: str
    chunk_count: int
    metadata_json: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int
    page: int
    page_size: int
