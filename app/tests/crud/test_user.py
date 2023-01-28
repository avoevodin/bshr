import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.core.security import verify_password
from app.tests.utils.utils import random_email, random_lower_string


@pytest.mark.asyncio
async def test_create_user(db: AsyncSession) -> None:
    """
    Test create user crud operation.

    Args:
        db: SQLAlchemy session

    Returns:
        None
    """
    username = random_lower_string(12)
    email = random_email()
    password = random_lower_string()
    user_in = schemas.UserCreate(username=username, email=email, password=password)
    user = await crud.user.create(db, obj_in=user_in)
    assert user.username == username
    assert user.email == email
    assert hasattr(user, "password")
    assert verify_password(password, user.password)


@pytest.mark.asyncio
async def test_get_user_by_email(
    db: AsyncSession, some_user_for_session: models.User
) -> None:
    """
    Test get user by email crud operation.

    Args:
        db: SQLAlchemy session
        some_user_for_session: random user created in db
    Returns:
        None
    """
    user_by_email = await crud.user.get_by_email(db, email=some_user_for_session.email)
    assert some_user_for_session == user_by_email


@pytest.mark.asyncio
async def test_get_user_by_username(
    db: AsyncSession, some_user_for_session: models.User
) -> None:
    """
    Test get user by username crud operation.

    Args:
        db: SQLAlchemy session
        some_user_for_session: random user created in db
    Returns:
        None
    """
    user_by_username = await crud.user.get_by_username(
        db, username=some_user_for_session.username
    )
    assert some_user_for_session == user_by_username


@pytest.mark.asyncio
async def test_update_user(
    db: AsyncSession, some_user_for_function: models.User
) -> None:
    """
    Test user update crud operation.

    Args:
        db: SQLAlchemy session

    Returns:
        None
    """

    password = random_lower_string(8)
    user_update_data = schemas.UserUpdate(
        email=random_email(),
        username=random_lower_string(8),
        password=password,
        is_active=False,
    )
    user_db_upd = await crud.user.update(
        db, obj_db=some_user_for_function, obj_in=user_update_data
    )
    assert user_db_upd.email == user_update_data.email
    assert user_db_upd.username == user_update_data.username
    assert user_db_upd.is_active == user_update_data.is_active
    assert verify_password(password, user_db_upd.password)


def test_user_is_active_by_default(some_user_for_session: models.User) -> None:
    """
    Test user is active by default.

    Args:
        some_user_for_session: random user created in db

    Returns:
        None
    """
    assert crud.user.is_active(some_user_for_session)


def test_user_is_not_superuser_by_default(some_user_for_session: models.User) -> None:
    """
    Test user is not superuser by default.

    Args:
        some_user_for_session: random user created in db

    Returns:
        None
    """
    assert not crud.user.is_superuser(some_user_for_session)


@pytest.mark.asyncio
async def test_authenticate_by_email_success(db) -> None:
    """
    Test success authentication by email.

    Args:
        db: SQLAlchemy async session

    Returns:
        None
    """
    password = random_lower_string(8)
    email = random_email()
    user_data = schemas.UserCreate(
        email=email, username=random_lower_string(8), password=password
    )
    user_db = await crud.user.create(db, obj_in=user_data)
    user_auth = await crud.user.authenticate_by_email(
        db, email=email, password=password
    )
    assert user_db == user_auth


@pytest.mark.asyncio
async def test_authenticate_by_email_fail_invalid_password(db) -> None:
    """
    Test fail authentication with invalid password.

    Args:
        db: SQLAlchemy async session

    Returns:
        None
    """
    password = random_lower_string(8)
    email = random_email()
    user_data = schemas.UserCreate(
        email=email, username=random_lower_string(8), password=password
    )
    await crud.user.create(db, obj_in=user_data)
    user_auth = await crud.user.authenticate_by_email(
        db, email=email, password="wrong_password"
    )
    assert user_auth is None


@pytest.mark.asyncio
async def test_authenticate_by_email_fail_invalid_email(db) -> None:
    """
    Test fail authentication with invalid email.

    Args:
        db: SQLAlchemy async session

    Returns:
        None
    """
    password = random_lower_string(8)
    email = random_email()
    user_data = schemas.UserCreate(
        email=email, username=random_lower_string(8), password=password
    )
    await crud.user.create(db, obj_in=user_data)
    user_auth = await crud.user.authenticate_by_email(
        db, email="wrong_email@example.com", password=password
    )
    assert user_auth is None
