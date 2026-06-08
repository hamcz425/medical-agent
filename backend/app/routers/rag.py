from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.document import Document
from app.models.query_log import QueryLog
from app.schemas.query import (
    QueryRequest, QueryResponse, SourceDocument, VerificationResult,
    QueryHistoryResponse, FeedbackRequest, FeedbackResponse, SystemStats
)
from app.services.auth_service import get_current_user
from app.services.rag_engine import rag_engine

router = APIRouter(prefix="/api/rag", tags=["RAG Query"])


async def _build_sources_from_ids(source_doc_ids: str, db: AsyncSession) -> list[SourceDocument]:
    if not source_doc_ids:
        return []
    doc_ids = [int(did) for did in source_doc_ids.split(",") if did.strip()]
    if not doc_ids:
        return []
    result = await db.execute(select(Document).where(Document.id.in_(doc_ids)))
    docs = result.scalars().all()
    doc_map = {d.id: d for d in docs}
    sources = []
    for did in doc_ids:
        if did in doc_map:
            doc = doc_map[did]
            preview = doc.content[:200] + "..." if len(doc.content) > 200 else doc.content
            sources.append(SourceDocument(
                id=doc.id,
                title=doc.title,
                category=doc.category,
                source=doc.source,
                content_preview=preview
            ))
    return sources


@router.post("/query", response_model=QueryResponse)
async def query_rag(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await rag_engine.query(
        query_text=request.query,
        top_k=request.top_k,
        retrieval_mode=request.retrieval_mode,
        db=db,
        user_id=current_user.id
    )

    sources = [
        SourceDocument(
            id=s["id"],
            title=s["title"],
            category=s["category"],
            source=s.get("source"),
            content_preview=s["content_preview"],
            rrf_score=s.get("rrf_score")
        )
        for s in result["sources"]
    ]

    verification = None
    if result.get("verification"):
        verification = VerificationResult(**result["verification"])

    return QueryResponse(
        id=result.get("id", 0),
        query=request.query,
        response=result["response"],
        confidence=result["confidence"],
        processing_time=result["processing_time"],
        sources=sources,
        retrieval_mode=result.get("retrieval_mode", "hybrid"),
        verification=verification,
        created_at=datetime.now(timezone.utc)
    )


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(QueryLog).where(
            QueryLog.id == request.query_log_id,
            QueryLog.user_id == current_user.id
        )
    )
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="Query log not found")

    log.doctor_feedback = request.rating
    log.feedback_comment = request.comment
    log.corrected_response = request.corrected_response
    log.feedback_at = datetime.now(timezone.utc)

    await db.commit()
    return FeedbackResponse(success=True, message="反馈提交成功")


@router.get("/history", response_model=QueryHistoryResponse)
async def get_query_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(QueryLog)
        .where(QueryLog.user_id == current_user.id)
        .order_by(QueryLog.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    logs = result.scalars().all()

    count_result = await db.execute(
        select(func.count(QueryLog.id)).where(QueryLog.user_id == current_user.id)
    )
    total = count_result.scalar() or 0

    queries = []
    for log in logs:
        sources = await _build_sources_from_ids(log.source_doc_ids, db)
        queries.append(QueryResponse(
            id=log.id,
            query=log.query,
            response=log.response or "",
            confidence=log.confidence,
            processing_time=log.processing_time,
            sources=sources,
            retrieval_mode=log.retrieval_mode,
            created_at=log.created_at
        ))

    return QueryHistoryResponse(queries=queries, total=total)


@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.services.document_service import DocumentService
    doc_service = DocumentService(db)
    doc_stats = await doc_service.get_stats()

    total_queries = await db.execute(select(func.count(QueryLog.id)))
    avg_time = await db.execute(select(func.avg(QueryLog.processing_time)))

    recent = await db.execute(
        select(QueryLog).order_by(QueryLog.created_at.desc()).limit(5)
    )
    recent_logs = recent.scalars().all()

    recent_queries = []
    for log in recent_logs:
        sources = await _build_sources_from_ids(log.source_doc_ids, db)
        recent_queries.append(QueryResponse(
            id=log.id,
            query=log.query,
            response=log.response or "",
            confidence=log.confidence,
            processing_time=log.processing_time,
            sources=sources,
            retrieval_mode=log.retrieval_mode,
            created_at=log.created_at
        ))

    return SystemStats(
        total_documents=doc_stats["total_documents"],
        processed_documents=doc_stats["processed_documents"],
        indexed_documents=doc_stats["indexed_documents"],
        total_queries=total_queries.scalar() or 0,
        average_response_time=float(avg_time.scalar() or 0),
        system_health="healthy",
        document_categories=doc_stats["document_categories"],
        recent_queries=recent_queries
    )
