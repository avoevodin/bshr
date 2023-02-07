import json

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from pydantic import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import schemas, crud
from app.tests.utils.utils import random_lower_string, random_email


@pytest.mark.asyncio
async def test_login_access_token(
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
    assert token.get("access_token")
    assert token.get("refresh_token")
    assert token.get("token_type") == "bearer"
