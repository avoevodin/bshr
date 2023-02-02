"""
Redis database initialization methods.

Attrs:
    app_init_redis: redis initialization.
    app_dispose_redis: redis disposing.
    get_redis_key: get redis value by key.
    set_redis_key: set redis value.
"""
from typing import Optional

import redis.asyncio as async_redis
from fastapi import FastAPI
from redis.asyncio import Redis

from app.core.config import settings


async def app_init_redis(app: FastAPI) -> None:
    """
    Init redis connection pool.

    Args:
        app: FastAPI application.

    Returns:
        None
    """
    app.state.redis = async_redis.from_url(settings.REDIS_DATABASE_URI)


async def app_dispose_redis(app: FastAPI) -> None:
    """
    Dispose redis connection pool.

    Args:
        app: FastAPI application.

    Returns:
        None
    """
    await app.state.redis.close()


async def get_redis_key(redis: Redis, key: str) -> Optional[str]:
    """
    Read redis key.

    Args:
        redis: redis database connection
        key: redis key

    Returns:
        value if key is found, None - otherwise.
    """
    async with redis.client() as conn:
        val = await conn.get(key)
    return val


async def set_redis_key(
    redis: Redis, key: str, value: str, expire: Optional[int] = None
) -> bool:
    """
    Set redis key with expiration.

    Args:
        redis: redis database connection
        key: key to set
        value: value to set
        expire: expiration time (seconds)

    Returns:
        True - success, False - otherwise
    """
    async with redis.client() as conn:
        if expire is None:
            res = await conn.set(key, value)
        else:
            res = await conn.set(key, value, ex=expire)
    return res
