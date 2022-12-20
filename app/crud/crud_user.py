"""
User CRUD methods.
"""
from typing import Optional, Union, Dict, Any

from sqlalchemy.future import select
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models import User
from schemas import UserCreate, UserUpdate
from core.security import password_hash_ctx


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """
        Get user by email.

        :param db: SQLAlchemy session
        :param email: email string
        :return: User
        """
        res = await db.execute(select(self.model).filter(self.model.email == email))
        found_user = res.scalar_one_or_none()
        return found_user

    async def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """
        Get user by username.

        :param db: SQLAlchemy session
        :param username: username string
        :return: User
        """
        res = await db.execute(
            select(self.model).filter(self.model.username == username)
        )
        found_user = res.scalar_one_or_none()
        return found_user

    async def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Create user.

        :param db: SQLAlchemy session
        :param obj_in: user create schema
        :return:  user model
        """
        obj_in.password = password_hash_ctx.hash(obj_in.password)
        user_db = User(**obj_in.dict())
        db.add(user_db)
        await db.commit()
        await db.refresh(user_db)
        return user_db

    async def update(
        self, db: Session, *, obj_db: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """
        Update user.

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

        obj_db = await super().update(db, obj_db=obj_db, obj_in=update_data)
        return obj_db

    async def authenticate_by_email(
        self, db: Session, *, email: str, password: str
    ) -> Optional[User]:
        """
        TODO
        Authenticate user by email.

        :param db: SQLAlchemy session
        :param email: user email string
        :param password: password
        :return:
        """
        pass

    async def authenticate_by_username(
        self, db: Session, *, username: str, password: str
    ):
        """
        TODO
        Authenticate user by username.

        :param db: SQLAlchemy session
        :param email: user email string
        :param password: password
        :return:
        """
        pass


@staticmethod
def is_active(usr: User) -> bool:
    """
    Check if user is active.
    :param usr: user object
    :return: bool
    """
    return usr.is_active


@staticmethod
def is_superuser(usr: User) -> bool:
    """
    Check if user is superuser.
    :param usr: user object
    :return: bool
    """
    return usr.is_superuser


user = CRUDUser(User)
