import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import schemas, crud
from app.core.security import verify_password
from app.tests.utils.utils import random_lower_string, random_email


@pytest.mark.asyncio
async def test_user_register_success(
    db: AsyncSession,
    get_client: AsyncClient,
    get_app: FastAPI,
) -> None:
    password = random_lower_string(8)
    user_data = schemas.UserCreate(
        username=random_lower_string(8),
        email=random_email(),
        password=password,
    )
    response = await get_client.post(
        get_app.url_path_for("users:register"), content=user_data.json()
    )
    assert response.status_code == status.HTTP_200_OK
    user_db = await crud.user.get_by_email(db, email=user_data.email)
    assert user_db
    assert user_db.email == user_data.email
    assert user_db.username == user_data.username
    assert verify_password(user_data.password, user_db.password)


@pytest.mark.asyncio
async def test_user_register_username_success(
    db: AsyncSession,
    get_client: AsyncClient,
    get_app: FastAPI,
) -> None:
    password = random_lower_string(8)
    user_data = schemas.UserCreate(
        username=random_lower_string(8),
        password=password,
    )
    response = await get_client.post(
        get_app.url_path_for("users:register"), content=user_data.json()
    )
    assert response.status_code == status.HTTP_200_OK
    user_db = await crud.user.get_by_username(db, username=user_data.username)
    assert user_db
    assert user_db.email == user_data.email
    assert user_db.username == user_data.username
    assert verify_password(user_data.password, user_db.password)


@pytest.mark.asyncio
async def test_user_register_email_success(
    db: AsyncSession,
    get_client: AsyncClient,
    get_app: FastAPI,
) -> None:
    password = random_lower_string(8)
    user_data = schemas.UserCreate(
        username=random_lower_string(8),
        email=random_email(),
        password=password,
    )
    response = await get_client.post(
        get_app.url_path_for("users:register"), content=user_data.json()
    )
    assert response.status_code == status.HTTP_200_OK
    user_db = await crud.user.get_by_username(db, username=user_data.username)
    assert user_db
    assert user_db.email == user_data.email
    assert user_db.username == user_data.username
    assert verify_password(user_data.password, user_db.password)
