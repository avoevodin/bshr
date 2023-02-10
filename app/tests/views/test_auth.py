import json

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from pydantic import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import schemas, crud
from app.core import auth
from app.core.auth import create_access_token
from app.schemas import TokenSubject, TokenPayload
from app.tests.utils.utils import random_lower_string, random_email


@pytest.mark.asyncio
async def test_login_access_token_username(
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
    user_db = await crud.user.create(db, obj_in=user_data)

    response = await get_client.post(
        get_app.url_path_for("auth:token"),
        data={"username": user_data.username, "password": password},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == status.HTTP_200_OK
    token = response.json()
    assert "access_token" in token
    assert "refresh_token" in token
    assert token.get("token_type") == "bearer"


@pytest.mark.asyncio
async def test_login_access_token_user_not_exist(
    db: AsyncSession,
    get_client: AsyncClient,
    get_app: FastAPI,
) -> None:
    password = random_lower_string(8)
    username = random_lower_string(8)

    response = await get_client.post(
        get_app.url_path_for("auth:token"),
        data={"username": username, "password": password},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_login_access_token_email(
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
    user_db = await crud.user.create(db, obj_in=user_data)

    response = await get_client.post(
        get_app.url_path_for("auth:token"),
        data={"username": user_data.email, "password": password},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == status.HTTP_200_OK
    token = response.json()
    assert "access_token" in token
    assert "refresh_token" in token
    assert token.get("token_type") == "bearer"


@pytest.mark.asyncio
async def test_login_access_token_fail_user_inactive(
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
    user_db = await crud.user.create(db, obj_in=user_data)
    user_update_data = schemas.user.UserUpdate(is_active=False)
    await crud.user.update(db, obj_db=user_db, obj_in=user_update_data)

    response = await get_client.post(
        get_app.url_path_for("auth:token"),
        data={"username": user_data.email, "password": password},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_login_access_token_superuser(
    settings_with_test_env: BaseSettings,
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
    user_db = await crud.user.create(db, obj_in=user_data)
    user_update_data = schemas.user.UserUpdate(is_superuser=True)
    await crud.user.update(db, obj_db=user_db, obj_in=user_update_data)

    response = await get_client.post(
        get_app.url_path_for("auth:token"),
        data={
            "username": settings_with_test_env.FIRST_SUPERUSER,
            "password": settings_with_test_env.FIRST_SUPERUSER_PASSWORD,
        },
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == status.HTTP_200_OK
    token = response.json()
    assert "access_token" in token
    assert "refresh_token" in token
    assert token.get("token_type") == "bearer"


@pytest.mark.asyncio
async def test_login_refresh_token(
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
    user_db = await crud.user.create(db, obj_in=user_data)

    response = await get_client.post(
        get_app.url_path_for("auth:token"),
        data={"username": user_data.username, "password": password},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == status.HTTP_200_OK
    token = response.json()
    assert "refresh_token" in token
    refresh_token = token["refresh_token"]
    payload = auth.decode_token(refresh_token)
    token_data = TokenPayload.parse_obj(payload)
    token_sub = TokenSubject.parse_obj(json.loads(token_data.sub))
    token_sub.id = 0
    refresh_token = create_access_token(token_sub)

    response = await get_client.post(
        get_app.url_path_for("auth:token-refresh"),
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    token = response.json()
    assert "access_token" in token
    assert "refresh_token" in token
    assert token.get("token_type") == "refresh_token"
    assert (
        len(token.get("access_token").split(".")) == 3
    ), "JWT token should have 3 segments"
    assert (
        len(token.get("refresh_token").split(".")) == 3
    ), "JWT token should have 3 segments"