from typing import Optional

from sqlalchemy.future import select
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from schemas import User, UserCreate, UserUpdate


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
