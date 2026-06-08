from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.models.document import Document
from app.config import get_settings

settings = get_settings()


class DocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        page: int = 1,
        page_size: int = 10,
        category: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[list[Document], int]:
        query = select(Document)

        if category:
            query = query.where(Document.category == category)
        if status:
            query = query.where(Document.status == status)
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Document.title.ilike(search_pattern),
                    Document.content.ilike(search_pattern),
                    Document.source.ilike(search_pattern)
                )
            )

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(Document.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        documents = result.scalars().all()

        return documents, total

    async def get_by_id(self, doc_id: int) -> Optional[Document]:
        result = await self.db.execute(select(Document).where(Document.id == doc_id))
        return result.scalar_one_or_none()

    async def create(self, doc_data: dict) -> Document:
        document = Document(**doc_data)
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def update(self, doc_id: int, update_data: dict) -> Optional[Document]:
        document = await self.get_by_id(doc_id)
        if not document:
            return None

        for key, value in update_data.items():
            if value is not None and hasattr(document, key):
                setattr(document, key, value)

        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def delete(self, doc_id: int) -> bool:
        document = await self.get_by_id(doc_id)
        if not document:
            return False

        await self.db.delete(document)
        await self.db.commit()
        return True

    async def get_stats(self) -> dict:
        total = await self.db.execute(select(func.count(Document.id)))
        processed = await self.db.execute(
            select(func.count(Document.id)).where(Document.status.in_(["processed", "indexed"]))
        )
        indexed = await self.db.execute(
            select(func.count(Document.id)).where(Document.status == "indexed")
        )

        categories = await self.db.execute(
            select(Document.category, func.count(Document.id)).group_by(Document.category)
        )
        category_counts = {row[0]: row[1] for row in categories.all()}

        return {
            "total_documents": total.scalar() or 0,
            "processed_documents": processed.scalar() or 0,
            "indexed_documents": indexed.scalar() or 0,
            "document_categories": category_counts
        }
