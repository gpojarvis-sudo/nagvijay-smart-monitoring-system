"""
Base Repository - Generic CRUD with async SQLAlchemy
"""
from __future__ import annotations

import uuid
from typing import Generic, TypeVar, Type, Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from sqlalchemy.orm import DeclarativeBase

ModelType = TypeVar("ModelType", bound=DeclarativeBase)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db
    
    def _generate_id(self) -> str:
        return str(uuid.uuid4())
    
    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        obj_in = obj_in.copy()
        if "id" not in obj_in:
            obj_in["id"] = self._generate_id()
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def get_by_id(self, id: str) -> Optional[ModelType]:
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> tuple[List[ModelType], int]:
        query = select(self.model)
        count_query = select(func.count()).select_from(self.model)
        
        # Apply filters
        if filters:
            for key, value in filters.items():
                if value is not None and hasattr(self.model, key):
                    col = getattr(self.model, key)
                    if isinstance(value, str) and key in ["office_name", "full_name", "email", "scheme_name"]:
                        query = query.where(col.ilike(f"%{value}%"))
                        count_query = count_query.where(col.ilike(f"%{value}%"))
                    else:
                        query = query.where(col == value)
                        count_query = count_query.where(col == value)
        
        # Total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Ordering
        if hasattr(self.model, order_by):
            order_col = getattr(self.model, order_by)
            if order_desc:
                query = query.order_by(order_col.desc())
            else:
                query = query.order_by(order_col.asc())
        
        # Pagination
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        items = list(result.scalars().all())
        
        return items, total
    
    async def update(self, id: str, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return None
        for key, value in obj_in.items():
            if value is not None and hasattr(db_obj, key):
                setattr(db_obj, key, value)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def delete(self, id: str) -> bool:
        result = await self.db.execute(delete(self.model).where(self.model.id == id))
        await self.db.flush()
        return result.rowcount > 0
    
    async def exists(self, **kwargs) -> bool:
        query = select(func.count()).select_from(self.model)
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        result = await self.db.execute(query)
        count = result.scalar() or 0
        return count > 0
