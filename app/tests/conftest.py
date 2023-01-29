"""
Pytest application configuration.

Args:
    - engine (database engine instance with applied migrations)
"""
import asyncio
import pathlib
import sys
from asyncio import AbstractEventLoop
from typing import List

import pytest
import pytest_asyncio
from alembic.config import Config
from alembic.operations import Operations
from alembic.runtime.environment import EnvironmentContext
from alembic.runtime.migration import MigrationContext, RevisionStep
from alembic.script import ScriptDirectory
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.future import Connection
from sqlalchemy.orm import sessionmaker

from app import crud, models, schemas
from app.db import Base
from app.tests.utils.utils import random_email, random_lower_string

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


async def disconnect(engine: AsyncEngine) -> None:
    """
    Dispose a database engine and destroy all of its connections.

    Args:

    Returns:
        None
    """

    await engine.dispose()


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
async def get_app() -> FastAPI:
    """
    Creates FastAPI test application with initialized databases.

    Returns:
        FastAPI wsgi application instance
    """
    from app.main import app

    async with LifespanManager(app):
        yield app


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
