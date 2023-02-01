from unittest import mock

import pytest
from httpx import AsyncClient
from pydantic import BaseSettings
from starlette import status


@pytest.mark.asyncio
async def test_read_main(settings_with_test_env: BaseSettings, get_client: AsyncClient):
    settings = settings_with_test_env
    with mock.patch("app.db.redis.get_redis_key", return_value=0) as redis_get:
        response = await get_client.get(f"{settings.API_PREFIX}/utils/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"detail": "OK"}
