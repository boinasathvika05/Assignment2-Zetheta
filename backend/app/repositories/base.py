from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models.base import TimeStampedModel

ModelType = TypeVar("ModelType", bound=TimeStampedModel)


class BaseRepository(Generic[ModelType]):
    """
    Generic Async CRUD Repository providing standard database operations following Clean Architecture.
    """
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id: str) -> Optional[ModelType]:
        """Fetch entity by primary key ID (excluding soft-deleted)."""
        stmt = select(self.model).where(self.model.id == id, self.model.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create(self, obj_in: Dict[str, Any] | ModelType) -> ModelType:
        """Create new entity in DB."""
        if isinstance(obj_in, dict):
            db_obj = self.model(**obj_in)
        else:
            db_obj = obj_in
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: ModelType, obj_in: Dict[str, Any]) -> ModelType:
        """Update existing entity fields."""
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def soft_delete(self, id: str) -> bool:
        """Soft delete entity by setting is_deleted=True."""
        stmt = update(self.model).where(self.model.id == id).values(is_deleted=True)
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount > 0

    async def list_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """List active entities with pagination."""
        stmt = select(self.model).where(self.model.is_deleted == False).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
