import pytest
from sqlalchemy.orm import Session

from app import crud
from app.core.security import password_hash_ctx
from app.schemas.user import UserCreate
from app.tests.utils.utils import random_email, random_lower_string


@pytest.mark.asyncio
async def test_create_user(db: Session) -> None:
    """
    Test create user crud operation

    Args:
        db: SQLAlchemy session

    Returns:
        None
    """
    username = random_lower_string(12)
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(username=username, email=email, password=password)
    user = await crud.user.create(db, obj_in=user_in)
    assert user.username == username
    assert user.email == email
    assert hasattr(user, "password")
    assert password_hash_ctx.hash(password) == user.password
