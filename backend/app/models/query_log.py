from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Text, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class QueryLog(Base):
    __tablename__ = "query_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    processing_time: Mapped[int] = mapped_column(Integer, default=0)
    source_doc_ids: Mapped[str] = mapped_column(Text, nullable=True)
    retrieval_mode: Mapped[str] = mapped_column(String(20), default="hybrid")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    doctor_feedback: Mapped[str] = mapped_column(String(20), nullable=True)
    feedback_comment: Mapped[str] = mapped_column(Text, nullable=True)
    corrected_response: Mapped[str] = mapped_column(Text, nullable=True)
    feedback_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    user = relationship("User", back_populates="query_logs", lazy="selectin")

    def __repr__(self):
        return f"<QueryLog(id={self.id}, query={self.query[:30]}...)>"
