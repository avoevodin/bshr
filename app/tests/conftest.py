"""
Pytest application configuration.

Args:
    - engine (database engine instance with applied migrations)
"""
import asyncio
import os
import pathlib
import sys
from asyncio import AbstractEventLoop
from typing import List
from unittest import mock

import pytest
import pytest_asyncio
import redis.asyncio as async_redis
from alembic.config import Config
from alembic.operations import Operations
from alembic.runtime.environment import EnvironmentContext
from alembic.runtime.migration import MigrationContext, RevisionStep
from alembic.script import ScriptDirectory
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient
from pydantic import BaseSettings
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.future import Connection
from sqlalchemy.orm import sessionmaker

from app import crud, models, schemas
from app.db import Base
from app.tests.utils.utils import (
    random_email,
    random_lower_string,
    get_settings_env_dict,
)

BASE_PATH = pathlib.Path(__file__).parent.parent
sys.path.append(str(BASE_PATH))


def do_upgrade(revision: str, context: MigrationContext) -> List[RevisionStep]:
    """
    Apply revision to context.

    Args:
        revision: current revision
        context: revision apply context

    Returns:
        list of revision steps
    """
    alembic_script = context.script
    return alembic_script._upgrade_revs(alembic_script.get_heads(), revision)  # noqa


def do_run_migrations(connection: Connection, alembic_env: EnvironmentContext) -> None:
    """
    Run migrations.

    Args:
        connection: database connection
        alembic_env: alembic environment

    Returns:
        None
    """
    alembic_env.configure(
        connection=connection,
        target_metadata=Base.metadata,
        fn=do_upgrade,
        render_as_batch=True,
    )
    migration_context = alembic_env.get_context()

    with migration_context.begin_transaction():
        with Operations.context(migration_context):
            migration_context.run_migrations()


async def async_migrate(engine: AsyncEngine, alembic_env: EnvironmentContext) -> None:
    """
    Apply all migrations.

    Args:
        engine: async engine with connection
        alembic_env: alembic environment context

    Returns:
        None
    """
    async with engine.begin() as conn:
        await conn.run_sync(do_run_migrations, alembic_env)


async def migrate(engine: AsyncEngine, url: str) -> None:
    """
    Read alembic config and create environment context.

    Args:
        engine: async engine with connection
        url: url connection string

    Returns:
        None
    """
    alembic_conf = Config()
    alembic_conf.set_main_option("script_location", f"{BASE_PATH}/alembic")
    alembic_conf.set_main_option("url", url)
    alembic_script = ScriptDirectory.from_config(alembic_conf)
    alembic_env = EnvironmentContext(alembic_conf, alembic_script)

    await async_migrate(engine, alembic_env)


@pytest_asyncio.fixture(scope="session")
async def db(engine: AsyncEngine) -> AsyncSession:
    """
    Create async engine and run alembic migrations on database.

    Returns:
        sqlalchemy async session
    """
    async_session = sessionmaker(
        engine, expire_on_commit=False, autoflush=False, class_=AsyncSession
    )
    async with async_session(bind=engine) as session:
        yield session


@pytest.fixture(scope="session")
def event_loop() -> AbstractEventLoop:
    """Redefinition of base pytest-asyncio event_loop fixture.

    Redefinition of base pytest-asyncio event_loop fixture,
    which returns the same value but with scope session.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()

    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def get_redis(redis_test_url: str) -> Redis:
    """
    Creates redis test connection pool with url connection string provided.

    Args:
        redis_test_url: url string

    Returns:
        Redis instance
    """
    return async_redis.from_url(redis_test_url)


@pytest_asyncio.fixture(scope="session")
async def get_app(
    engine: AsyncEngine,
    db_test_url: str,
    get_redis: Redis,
    redis_test_url: str,
    settings_env_dict_session_scope: dict,
) -> FastAPI:
    """
    Creates FastAPI test application with initialized databases.

    Args:
        engine: async database engine instance
        database_test_url: db connection url
        get_redis: redis instance
        redis_test_url: redis connection instance
        test_settings_env_dict: test env vars for settings

    Returns:
        FastAPI wsgi application instance
    """
    with mock.patch.dict(os.environ, settings_env_dict_session_scope):
        with mock.patch(
            "sqlalchemy.ext.asyncio.create_async_engine", return_value=engine
        ) as create_eng:
            with mock.patch(
                "redis.asyncio.from_url", return_value=get_redis
            ) as create_redis:
                with mock.patch("app.db.redis.get_redis_key", return_value=0):
                    create_eng.return_value = engine
                    create_redis.return_value = get_redis
                    from app.main import app

                    async with LifespanManager(app):
                        yield app


@pytest_asyncio.fixture(scope="session")
async def get_client(get_app: FastAPI) -> AsyncClient:
    """
    Create a custom async http client based on httpx AsyncClient.

    Args:
        get_app: FastAPI wsgi application instance

    Returns:
        httpx async client instance
    """
    async with AsyncClient(app=get_app, base_url="http://testserver") as client:
        yield client


@pytest.fixture(scope="session")
def db_test_url() -> str:
    """
    Generate in memory sqlite db connect url for test purposes.

    Returns:
        url string for test database connection
    """
    return "sqlite+aiosqlite://?cache=shared"  # noqa


@pytest.fixture(scope="session")
def redis_test_url() -> str:
    """
    Generate test string for redis connection.

    Returns:
        url string for redis test database connection
    """
    return "redis://127.0.0.1:6379/0"  # noqa


@pytest.fixture(scope="function")
def settings_env_dict_function_scope() -> dict:
    """
    Return test settings env dict for function scope.

    Returns:
        dict of envs
    """
    return get_settings_env_dict()


@pytest.fixture(scope="session")
def settings_env_dict_session_scope() -> dict:
    """
    Return test settings env dict for function scope.

    Returns:
        dict of envs
    """
    return get_settings_env_dict()


@pytest.fixture(scope="function")
def settings_with_test_env(settings_env_dict_function_scope: dict) -> BaseSettings:
    """
    Return test settings instance.

    Args:
        test_settings_env_dict_session_scope:

    Returns:
        test Settings instance
    """
    with mock.patch.dict(os.environ, settings_env_dict_function_scope):
        from app.core.config import settings

        return settings


@pytest_asyncio.fixture(scope="session")
async def engine(db_test_url: str) -> AsyncEngine:
    """
    Create async engine and run alembic migrations on database.

    Args:
        database_test_url: test db connection url

    Returns:
        SQLAlchemy async engine
    """
    url = db_test_url
    engine = create_async_engine(url, echo=False)
    await migrate(engine, url)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def some_user_for_session(db: AsyncSession) -> models.User:
    user_data = schemas.UserCreate(
        username=random_lower_string(8),
        email=random_email(),
        password=random_lower_string(8),
    )
    user_db = await crud.user.create(db, obj_in=user_data)
    return user_db


@pytest_asyncio.fixture(scope="function")
async def some_user_for_function(db: AsyncSession) -> models.User:
    user_data = schemas.UserCreate(
        username=random_lower_string(8),
        email=random_email(),
        password=random_lower_string(8),
    )
    user_db = await crud.user.create(db, obj_in=user_data)
    return user_db
