import re
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse, DocumentListResponse
from app.services.auth_service import get_current_user, require_role
from app.services.document_service import DocumentService

logger = logging.getLogger(__name__)

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.get("", response_model=DocumentListResponse)
async def get_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = DocumentService(db)
    documents, total = await service.get_all(
        page=page,
        page_size=page_size,
        category=category,
        status=status,
        search=search
    )
    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(doc) for doc in documents],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/stats/overview")
async def get_document_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = DocumentService(db)
    return await service.get_stats()


@router.post("/index-all")
async def index_all_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = require_role("admin", "doctor", "researcher")
):
    from app.services.rag_engine import rag_engine
    service = DocumentService(db)
    documents, total = await service.get_all(page=1, page_size=100, status="pending")
    all_results = []
    page_num = 1

    while documents:
        for doc in documents:
            try:
                chunk_count = await rag_engine.index_document(doc)
                await service.update(doc.id, {"status": "indexed", "chunk_count": chunk_count})
                all_results.append({"doc_id": doc.id, "title": doc.title, "chunk_count": chunk_count})
            except Exception as e:
                logger.warning("Failed to index doc %d: %s", doc.id, e)
                all_results.append({"doc_id": doc.id, "title": doc.title, "error": str(e)})

        page_num += 1
        documents, _ = await service.get_all(page=page_num, page_size=100, status="pending")

    return {"message": f"Indexed {len([r for r in all_results if 'chunk_count' in r])} documents", "results": all_results}


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    doc_data: DocumentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_role("admin", "doctor", "researcher")
):
    service = DocumentService(db)
    document = await service.create({
        **doc_data.model_dump(),
        "status": "pending",
        "chunk_count": 0
    })
    return DocumentResponse.model_validate(document)


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    category: str = Query(..., pattern="^(medical_record|research_paper|drug_info|clinical_guide)$"),
    source: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = require_role("admin", "doctor", "researcher")
):
    content = await file.read()

    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {MAX_UPLOAD_SIZE // (1024*1024)}MB")

    safe_filename = re.sub(r'[^\w\-_\. ]', '_', file.filename or "unknown")
    safe_filename = safe_filename.lstrip(". ")

    if safe_filename.endswith(".txt") or safe_filename.endswith(".md"):
        text = content.decode("utf-8", errors="replace")
    elif safe_filename.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            reader = PdfReader(file.file)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            raise HTTPException(status_code=400, detail="PDF parsing failed")
    elif safe_filename.endswith(".docx"):
        try:
            from docx import Document as DocxDocument
            import io
            doc = DocxDocument(io.BytesIO(content))
            text = "\n".join(para.text for para in doc.paragraphs)
        except Exception as e:
            raise HTTPException(status_code=400, detail="DOCX parsing failed")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use .txt, .md, .pdf, or .docx")

    if not text.strip():
        raise HTTPException(status_code=400, detail="File is empty or text could not be extracted")

    title = safe_filename.rsplit(".", 1)[0]

    service = DocumentService(db)
    document = await service.create({
        "title": title,
        "content": text,
        "category": category,
        "source": source or safe_filename,
        "file_type": safe_filename.rsplit(".", 1)[-1],
        "file_size": len(content),
        "status": "pending",
        "chunk_count": 0,
        "metadata_json": {"original_filename": safe_filename}
    })
    return DocumentResponse.model_validate(document)


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = DocumentService(db)
    document = await service.get_by_id(doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse.model_validate(document)


@router.put("/{doc_id}", response_model=DocumentResponse)
async def update_document(
    doc_id: int,
    update_data: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_role("admin", "doctor", "researcher")
):
    service = DocumentService(db)
    document = await service.update(doc_id, update_data.model_dump(exclude_unset=True))
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse.model_validate(document)


@router.post("/{doc_id}/index")
async def index_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_role("admin", "doctor", "researcher")
):
    from app.services.rag_engine import rag_engine
    service = DocumentService(db)
    document = await service.get_by_id(doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        chunk_count = await rag_engine.index_document(document)
        await service.update(doc_id, {"status": "indexed", "chunk_count": chunk_count})
        return {"message": f"Document indexed successfully", "doc_id": doc_id, "chunk_count": chunk_count}
    except Exception as e:
        logger.exception("Index failed for doc %d", doc_id)
        raise HTTPException(status_code=500, detail="Indexing failed")


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_role("admin")
):
    service = DocumentService(db)
    document = await service.get_by_id(doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        from app.services.rag_engine import rag_engine
        await rag_engine.delete_document(doc_id)
    except Exception as e:
        logger.warning("Failed to clean vector store for doc %d: %s", doc_id, e)

    await service.delete(doc_id)
