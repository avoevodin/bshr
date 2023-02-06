import os
from unittest import mock

import pytest

from app.tests.utils.utils import get_settings_env_dict

with mock.patch.dict(os.environ, get_settings_env_dict()):
    from app.db.redis import get_redis_key, set_redis_key


@pytest.mark.asyncio
async def test_redis_get() -> None:
    redis = mock.MagicMock()
    redis.client.return_value.__aenter__.return_value.get.return_value = True
    res = await get_redis_key(redis=redis, key="test key")
    redis.client.return_value.__aenter__.return_value.get.assert_called_once_with(
        "test key"
    )
    assert res


@pytest.mark.asyncio
async def test_set_redis_key() -> None:
    redis = mock.MagicMock()
    redis.client.return_value.__aenter__.return_value.set.return_value = True
    res = await set_redis_key(redis=redis, key="test key", value="test value")
    redis.client.return_value.__aenter__.return_value.set.assert_called_once_with(
        "test key", "test value"
    )
    assert res


@pytest.mark.asyncio
async def test_set_redis_key_with_expire() -> None:
    redis = mock.MagicMock()
    expire = 60 * 60
    redis.client.return_value.__aenter__.return_value.set.return_value = True
    res = await set_redis_key(
        redis=redis, key="test key", value="test value", expire=expire
    )
    redis.client.return_value.__aenter__.return_value.set.assert_called_once_with(
        "test key", "test value", ex=expire
    )
    assert res
