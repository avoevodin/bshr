import json

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from pydantic import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import schemas, crud, models
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


@pytest.mark.asyncio
async def test_user_register_twice(
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
    response = await get_client.post(
        get_app.url_path_for("users:register"), content=user_data.json()
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        f"User with email (username) {user_data.email} "
        f"({user_data.username}) already exists"
        in response.content.decode()
    )


@pytest.mark.asyncio
async def test_read_users_list_unauthorized(
    db: AsyncSession,
    get_client: AsyncClient,
    get_app: FastAPI,
) -> None:
    response = await get_client.get(get_app.url_path_for("users:read_users"))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in response.content.decode()


@pytest.mark.asyncio
async def test_read_users_list_permission_denied(
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
    response = await get_client.post(
        get_app.url_path_for("auth:token"),
        data={"username": user_data.username, "password": password},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    token = response.json()
    response = await get_client.get(
        get_app.url_path_for("users:read_users"),
        headers={"Authorization": f"Bearer {token.get('access_token')}"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "The user doesn't have enough privileges." in response.content.decode()


@pytest.mark.asyncio
async def test_read_users_list_success(
    db: AsyncSession,
    get_client: AsyncClient,
    get_app: FastAPI,
    settings_with_test_env: BaseSettings,
) -> None:
    user_data = schemas.UserCreate(
        username=settings_with_test_env.FIRST_SUPERUSER,
        email=settings_with_test_env.FIRST_SUPERUSER_EMAIL,
        password=settings_with_test_env.FIRST_SUPERUSER_PASSWORD,
    )
    response = await get_client.post(
        get_app.url_path_for("auth:token"),
        data={
            "username": user_data.username,
            "password": settings_with_test_env.FIRST_SUPERUSER_PASSWORD,
        },
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    token = response.json()
    response = await get_client.get(
        get_app.url_path_for("users:read_users"),
        headers={"Authorization": f"Bearer {token.get('access_token')}"},
    )
    users_list = await crud.user.get_multi(db)
    assert response.status_code == status.HTTP_200_OK
    assert len(json.loads(response.content.decode())) == len(users_list)


@pytest.mark.asyncio
async def test_update_unauthorized(
    db: AsyncSession,
    get_client: AsyncClient,
    get_app: FastAPI,
    settings_with_test_env: BaseSettings,
) -> None:
    response = await get_client.patch(get_app.url_path_for("users:update", user_id=-1))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in response.content.decode()


@pytest.mark.asyncio
async def test_update_not_found(
    db: AsyncSession,
    get_client: AsyncClient,
    get_app: FastAPI,
    settings_with_test_env: BaseSettings,
) -> None:
    user_data = schemas.UserCreate(
        username=settings_with_test_env.FIRST_SUPERUSER,
        email=settings_with_test_env.FIRST_SUPERUSER_EMAIL,
        password=settings_with_test_env.FIRST_SUPERUSER_PASSWORD,
    )
    response = await get_client.post(
        get_app.url_path_for("auth:token"),
        data={
            "username": user_data.username,
            "password": settings_with_test_env.FIRST_SUPERUSER_PASSWORD,
        },
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    user_update_data = schemas.UserUpdate(email=random_email())
    user_id = -1
    token = response.json()
    response = await get_client.patch(
        get_app.url_path_for("users:update", user_id=user_id),
        headers={"Authorization": f"Bearer {token.get('access_token')}"},
        content=user_update_data.json(),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert f"User with id <{user_id}> not found" in response.content.decode()


@pytest.mark.asyncio
async def test_update_with_superuser(
    db: AsyncSession,
    get_client: AsyncClient,
    get_app: FastAPI,
    settings_with_test_env: BaseSettings,
    some_user_for_function: models.User,
) -> None:
    response = await get_client.post(
        get_app.url_path_for("auth:token"),
        data={
            "username": settings_with_test_env.FIRST_SUPERUSER,
            "password": settings_with_test_env.FIRST_SUPERUSER_PASSWORD,
        },
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    user_update_data = schemas.UserUpdate(email=random_email())
    user_id = some_user_for_function.id
    token = response.json()
    response = await get_client.patch(
        get_app.url_path_for("users:update", user_id=user_id),
        headers={"Authorization": f"Bearer {token.get('access_token')}"},
        content=user_update_data.json(),
    )
    assert response.status_code == status.HTTP_200_OK
    await db.refresh(some_user_for_function)
    user_updated = json.loads(response.content.decode())
    assert some_user_for_function.email == user_updated.get("email")


@pytest.mark.asyncio
async def test_update_with_another_user(
    db: AsyncSession,
    get_client: AsyncClient,
    get_app: FastAPI,
    settings_with_test_env: BaseSettings,
    some_user_for_function: models.User,
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
    response = await get_client.post(
        get_app.url_path_for("auth:token"),
        data={
            "username": user_data.username,
            "password": password,
        },
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    user_update_data = schemas.UserUpdate(email=random_email())
    user_id = some_user_for_function.id
    token = response.json()
    response = await get_client.patch(
        get_app.url_path_for("users:update", user_id=user_id),
        headers={"Authorization": f"Bearer {token.get('access_token')}"},
        content=user_update_data.json(),
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "The user doesn't have enough privileges." in response.content.decode()


@pytest.mark.asyncio
async def test_update_success_current_user(
    db: AsyncSession,
    get_client: AsyncClient,
    get_app: FastAPI,
    settings_with_test_env: BaseSettings,
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
    user_data = schemas.User.parse_obj(json.loads(response.content.decode()))
    response = await get_client.post(
        get_app.url_path_for("auth:token"),
        data={
            "username": user_data.username,
            "password": password,
        },
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    user_update_data = schemas.UserUpdate(email=random_email())
    user_id = user_data.id
    token = response.json()
    response = await get_client.patch(
        get_app.url_path_for("users:update", user_id=user_id),
        headers={"Authorization": f"Bearer {token.get('access_token')}"},
        content=user_update_data.json(),
    )
    assert response.status_code == status.HTTP_200_OK
    user_updated_data = schemas.User.parse_obj(json.loads(response.content.decode()))
    assert user_id == user_updated_data.id
