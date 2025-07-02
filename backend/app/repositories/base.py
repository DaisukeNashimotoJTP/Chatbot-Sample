"""
Base repository class with common CRUD operations.
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations."""
    
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        """
        Initialize repository.
        
        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db
    
    async def get(self, id: UUID, include_deleted: bool = False) -> Optional[ModelType]:
        """
        Get record by ID.
        
        Args:
            id: Record ID
            include_deleted: Whether to include soft-deleted records
            
        Returns:
            Model instance or None
        """
        query = select(self.model).where(self.model.id == id)
        
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
        **filters
    ) -> List[ModelType]:
        """
        Get multiple records with pagination and filtering.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted records
            **filters: Additional filter conditions
            
        Returns:
            List of model instances
        """
        query = select(self.model)
        
        # Apply filters
        for field, value in filters.items():
            if hasattr(self.model, field):
                query = query.where(getattr(self.model, field) == value)
        
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))
        
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create(self, obj_in: Union[ModelType, Dict[str, Any]]) -> ModelType:
        """
        Create new record.
        
        Args:
            obj_in: Model instance or dictionary of attributes
            
        Returns:
            Created model instance
        """
        if isinstance(obj_in, dict):
            obj_in = self.model(**obj_in)
        
        self.db.add(obj_in)
        await self.db.commit()
        await self.db.refresh(obj_in)
        return obj_in
    
    async def update(
        self,
        id: UUID,
        obj_in: Union[Dict[str, Any], ModelType]
    ) -> Optional[ModelType]:
        """
        Update record by ID.
        
        Args:
            id: Record ID
            obj_in: Dictionary of attributes to update or model instance
            
        Returns:
            Updated model instance or None
        """
        # Get existing record
        db_obj = await self.get(id)
        if not db_obj:
            return None
        
        # Prepare update data
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        if update_data:
            # Update record
            query = (
                update(self.model)
                .where(self.model.id == id)
                .values(**update_data)
            )
            await self.db.execute(query)
            await self.db.commit()
            
            # Refresh and return updated record
            await self.db.refresh(db_obj)
        
        return db_obj
    
    async def delete(self, id: UUID, soft_delete: bool = True) -> bool:
        """
        Delete record by ID.
        
        Args:
            id: Record ID
            soft_delete: Whether to soft delete (set deleted_at) or hard delete
            
        Returns:
            True if deleted, False if not found
        """
        db_obj = await self.get(id)
        if not db_obj:
            return False
        
        if soft_delete and hasattr(db_obj, 'soft_delete'):
            # Soft delete
            db_obj.soft_delete()
            await self.db.commit()
        else:
            # Hard delete
            await self.db.delete(db_obj)
            await self.db.commit()
        
        return True
    
    async def count(self, include_deleted: bool = False, **filters) -> int:
        """
        Count records with optional filtering.
        
        Args:
            include_deleted: Whether to include soft-deleted records
            **filters: Filter conditions
            
        Returns:
            Number of records
        """
        query = select(self.model)
        
        # Apply filters
        for field, value in filters.items():
            if hasattr(self.model, field):
                query = query.where(getattr(self.model, field) == value)
        
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))
        
        result = await self.db.execute(query)
        return len(result.scalars().all())
    
    async def exists(self, id: UUID, include_deleted: bool = False) -> bool:
        """
        Check if record exists.
        
        Args:
            id: Record ID
            include_deleted: Whether to include soft-deleted records
            
        Returns:
            True if exists, False otherwise
        """
        obj = await self.get(id, include_deleted=include_deleted)
        return obj is not None