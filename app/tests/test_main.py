import importlib
import os
from functools import reduce
from unittest import mock

import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from pydantic import BaseSettings
from redis import Redis
from sqlalchemy.ext.asyncio import create_async_engine
from starlette import status
from starlette.middleware.cors import CORSMiddleware

from app.tests.utils.utils import get_settings_env_dict


@pytest.mark.asyncio
async def test_read_main(
    settings_with_test_env: BaseSettings, get_client: AsyncClient
) -> None:
    settings = settings_with_test_env
    response = await get_client.get(f"{settings.API_PREFIX}/utils/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"detail": "OK"}


@pytest.mark.asyncio
async def test_read_main_without_cors(
    get_redis: Redis, db_test_url: str, redis_test_url: str
) -> None:
    settings_dict = get_settings_env_dict()
    settings_dict["BACKEND_CORS_ORIGINS"] = "[]"
    url = db_test_url
    engine = create_async_engine(url, echo=False)
    with mock.patch.dict(os.environ, settings_dict):
        from app.core.config import Settings
        import app.core.config

        settings = Settings()
        with mock.patch.object(app.core.config, "settings", settings):
            with mock.patch(
                "sqlalchemy.ext.asyncio.create_async_engine", return_value=engine
            ) as create_eng:
                with mock.patch(
                    "redis.asyncio.from_url", return_value=get_redis
                ) as create_redis:
                    with mock.patch("app.db.redis.get_redis_key", return_value=0):
                        create_eng.return_value = engine
                        create_redis.return_value = get_redis
                        import app.main

                        importlib.reload(app.main)
                        from app.main import app

                        async with LifespanManager(app):
                            assert not app.user_middleware or not reduce(
                                lambda x: isinstance(x, CORSMiddleware),
                                app.user_middleware,
                            )
