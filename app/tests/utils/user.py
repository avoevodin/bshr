from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas, crud
from app.tests.utils.utils import random_lower_string, random_email


async def create_random_user(db: AsyncSession) -> models.User:
    """
    Create random user in db.

    Args:
        db: SQLAlchemy session

    Returns:
        created user
    """
    user_data = schemas.UserCreate(
        username=random_lower_string(8),
        email=random_email(),
        password=random_lower_string(8),
    )
    user_db = await crud.user.create(db, obj_in=user_data)
    return user_db
