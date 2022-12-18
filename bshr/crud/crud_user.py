from typing import Optional, Union, Dict, Any

from sqlalchemy.future import select
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models import User
from schemas import UserCreate, UserUpdate
from utils.password import password_hash_ctx


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """
        Get user by email.

        :param db: SQLAlchemy session
        :param email: email string
        :return: User
        """
        res = await db.execute(select(self.model).filter())
        found_user = res.scalar_one_or_none()
        return found_user

    async def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Create a user.

        :param db: SQLAlchemy session
        :param obj_in: user create schema
        :return:  user model
        """
        user_db = User(
            username=obj_in.username,
            email=obj_in.email,
            password=password_hash_ctx.hash(obj_in.password),
        )
        db.add(user_db)
        await db.commit()
        await db.refresh(user_db)
        return user_db

    async def update(
        self, db: Session, *, obj_db: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """

        :param db: SQLAlchemy session
        :param obj_db: user db model
        :param obj_in: user update data
        :return: user model
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        if update_data["password"]:
            hashed_password = password_hash_ctx.hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        return super().update(db, obj_db=obj_db, obj_in=update_data)
