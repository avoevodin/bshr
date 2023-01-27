"""
Common CRUD methods.
"""
from typing import TypeVar, Type, Generic, Optional, Any, List, Union, Dict

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base CRUD class.
    """

    def __init__(self, model: Type[ModelType]) -> None:
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        Args:
            model: SQLAlchemy model class
        """
        self.model = model

    async def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        Get one object from db if it's been found.

        Args:
            db: SQLAlchemy session
            id: object id

        Returns:
            SQLAlchemy model instance
        """
        res = await db.execute(select(self.model).filter(self.model.id == id))
        found_obj = res.scalar_one_or_none()
        return found_obj

    async def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple objects from db if they've been found.

        Args:
            db: SQLAlchemy session
            skip: ids to skip
            limit: max number of objects to return

        Returns:
            list of SQLAlchemy model instances
        """
        res = await db.execute(select(self.model).offset(skip).limit(limit))
        found_objs = res.scalars().all()
        return found_objs

    async def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create one object.

        Args:
            db: SQLAlchemy session
            obj_in: pydantic create schema type

        Returns:
            SQLAlchemy model instance.
        """
        obj_in_data = jsonable_encoder(obj_in)
        obj_db = self.model(**obj_in_data)
        db.add(obj_db)
        await db.commit()
        await db.refresh(obj_db)
        return obj_db

    async def update(
        self,
        db: Session,
        *,
        obj_db: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update an object with passed data.

        Args:
            db: SQLAlchemy session
            obj_db: SQLAlchemy model class
            obj_in: pydantic create schema type

        Returns:
            SQLAlchemy model instance
        """
        obj_data = jsonable_encoder(obj_db)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        for field in update_data:
            if field in obj_data:
                setattr(obj_db, field, update_data[field])

        db.add(obj_db)
        await db.commit()
        await db.refresh(obj_db)
        return obj_db

    async def remove(self, db: Session, *, id: int) -> ModelType:
        """
        Remove object by id.

        Args:
            db: SQLAlchemy session
            id: object id

        Returns:
            SQLAlchemy model instance
        """
        res = await db.execute(select(self.model).filter(self.model.id == id))
        found_obj = res.scalar_one_or_none()
        await db.delete(found_obj)
        await db.commit()
        return found_obj
