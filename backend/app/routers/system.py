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


@router.post("/seed")
async def manual_seed(db: AsyncSession = Depends(get_db)):
    from app.utils.auth import get_password_hash
    from app.models.document import Document

    result = await db.execute(select(User).where(User.username == "doctor1"))
    if result.scalar_one_or_none():
        return {"message": "doctor1 already exists", "status": "skipped"}

    doctor = User(
        username="doctor1",
        email="doctor1@hospital.com",
        hashed_password=get_password_hash("doctor123"),
        full_name="张医生",
        role="doctor",
        department="全科"
    )
    db.add(doctor)
    await db.commit()
    await db.refresh(doctor)

    return {"message": "doctor1 created", "id": doctor.id, "status": "created"}


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
