"""
User CRUD methods.
"""
from typing import Optional

from sqlalchemy.future import select
from sqlalchemy.orm import Session

from app.core.security import verify_password, get_password_hash
from app.crud.base import CRUDBase
from app.models import User
from app.schemas import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    User CRUD base class.
    """

    async def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            db: SQLAlchemy session
            email: email string

        Returns:
            optionally User model instance
        """
        res = await db.execute(select(self.model).filter(self.model.email == email))
        found_user = res.scalar_one_or_none()
        return found_user

    async def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """
        Get user by username.

        Args:
            db: SQLAlchemy session
            username: username string

        Returns:
            optionally User model instance
        """
        res = await db.execute(
            select(self.model).filter(self.model.username == username)
        )
        found_user = res.scalar_one_or_none()
        return found_user

    async def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Create user.

        Args:
            db: SQLAlchemy session
            obj_in: user create schema

        Returns:
            User model instance
        """
        obj_in.password = get_password_hash(obj_in.password)
        user_db = await super().create(db, obj_in=obj_in)
        return user_db

    async def update(self, db: Session, *, obj_db: User, obj_in: UserUpdate) -> User:
        """
        Update user.

        Args:
            db: SQLAlchemy session
            obj_db: user db model
            obj_in: user update data

        Returns:
            User model instance
        """
        if obj_in.password is not None:
            obj_in.password = get_password_hash(obj_in.password)

        obj_db = await super().update(db, obj_db=obj_db, obj_in=obj_in)
        return obj_db

    async def authenticate_by_email(
        self, db: Session, *, email: str, password: str
    ) -> Optional[User]:
        """
        Authenticate user by email.

        Args:
            db: SQLAlchemy session
            email: user email string
            password: password

        Returns:
            user if auth is success, None otherwise
        """
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    async def authenticate_by_username(
        self, db: Session, *, username: str, password: str
    ) -> Optional[User]:
        """
        Authenticate user by email.

        Args:
            db: SQLAlchemy session
            username: user email string
            password: password

        Returns:
            user if auth is success, None otherwise
        """
        user = await self.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    @staticmethod
    def is_active(usr: User) -> bool:
        """
        Check if user is active.

        Args:
            usr: user object

        Returns:
            true if user is active, false otherwise
        """
        return usr.is_active

    @staticmethod
    def is_superuser(usr: User) -> bool:
        """
        Check if user is superuser.

        Args:
            usr: user object

        Returns:
            true if user is superuser, false otherwise
        """
        return usr.is_superuser


user = CRUDUser(User)
