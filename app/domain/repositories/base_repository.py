from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from sqlmodel import SQLModel, Session, select, func, col
from sqlalchemy import asc, desc

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    model: Type[ModelType]

    def __init__(self, session: Session):
        self.session = session

    def create(self, obj_in: ModelType) -> ModelType:
        """Create a new record"""
        db_obj = self.model.model_validate(obj_in)
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def get_by_id(self, id: Any) -> Optional[ModelType]:
        """Get a single record by ID"""
        statement = select(self.model).where(self.model.id == id)
        return self.session.exec(statement).first()

    def get_all(
            self,
            skip: int = 0,
            limit: int = 100,
            sort_by: Optional[str] = None,
            sort_order: str = "asc"
    ) -> List[ModelType]:
        """Get all records with pagination and sorting"""
        statement = select(self.model)

        # Apply sorting
        if sort_by:
            order_func = asc if sort_order.lower() == "asc" else desc
            statement = statement.order_by(order_func(col(sort_by)))

        # Apply pagination
        statement = statement.offset(skip).limit(limit)

        return list(self.session.exec(statement).all())

    def get_with_filters(
            self,
            filters: Dict[str, Any],
            skip: int = 0,
            limit: int = 100,
            sort_by: Optional[str] = None,
            sort_order: str = "asc"
    ) -> List[ModelType]:
        """Get records with custom filters, pagination and sorting"""
        statement = select(self.model)

        # Apply filters
        for key, value in filters.items():
            if hasattr(self.model, key):
                statement = statement.where(getattr(self.model, key) == value)

        # Apply sorting
        if sort_by and hasattr(self.model, sort_by):
            order_func = asc if sort_order.lower() == "asc" else desc
            statement = statement.order_by(order_func(getattr(self.model, sort_by)))

        # Apply pagination
        statement = statement.offset(skip).limit(limit)

        return list(self.session.exec(statement).all())

    def get_one_with_filters(
            self,
            filters: Dict[str, Any]
    ) -> Optional[ModelType]:
        """Get a single record with custom filters"""
        statement = select(self.model)

        # Apply filters
        for key, value in filters.items():
            if hasattr(self.model, key):
                statement = statement.where(getattr(self.model, key) == value)

        return self.session.exec(statement).first()

    def update(self, id: Any, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """Update a record by ID"""
        db_obj = self.get_by_id(id)
        if not db_obj:
            return None

        for key, value in obj_in.items():
            if hasattr(db_obj, key):
                setattr(db_obj, key, value)

        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def delete(self, id: Any) -> bool:
        """Hard delete a record by ID"""
        db_obj = self.get_by_id(id)
        if not db_obj:
            return False

        self.session.delete(db_obj)
        self.session.commit()
        return True

    def soft_delete(self, id: Any) -> Optional[ModelType]:
        """Soft delete a record by ID (requires SoftDeleteMixin)"""
        db_obj = self.get_by_id(id)
        if not db_obj:
            return None

        if hasattr(db_obj, 'is_deleted'):
            db_obj.is_deleted = True
            if hasattr(db_obj, 'deleted_at'):
                from datetime import datetime, timezone
                db_obj.deleted_at = datetime.now(timezone.utc)

            self.session.add(db_obj)
            self.session.commit()
            self.session.refresh(db_obj)
            return db_obj

        return None

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count total records with optional filters"""
        statement = select(func.count()).select_from(self.model)

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    statement = statement.where(getattr(self.model, key) == value)

        return self.session.exec(statement).one()

    def exists(self, id: Any) -> bool:
        """Check if a record exists by ID"""
        return self.get_by_id(id) is not None

    def get_paginated(
            self,
            page: int = 1,
            page_size: int = 10,
            filters: Optional[Dict[str, Any]] = None,
            sort_by: Optional[str] = None,
            sort_order: str = "asc"
    ) -> Dict[str, Any]:
        """Get paginated results with metadata"""
        skip = (page - 1) * page_size

        items = self.get_with_filters(
            filters=filters or {},
            skip=skip,
            limit=page_size,
            sort_by=sort_by,
            sort_order=sort_order
        )

        total = self.count(filters=filters)
        total_pages = (total + page_size - 1) // page_size

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1
        }