from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.services.auth_service import get_current_user, require_role

router = APIRouter(prefix="/api/system", tags=["System"])


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }


@router.get("/metrics")
async def get_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = require_role("admin", "doctor", "viewer")
):
    from app.services.document_service import DocumentService
    doc_service = DocumentService(db)
    doc_stats = await doc_service.get_stats()

    return {
        "documents": doc_stats,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
