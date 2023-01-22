"""
Pytest application configuration.

Args:
    - engine (database engine instance with applied migrations)
"""
import asyncio
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
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.future import Connection

from app.db import Base
from app.db.session import engine, session
from app.utils.database import get_sqlalchemy_db_uri


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


async def async_migrate(alembic_env: EnvironmentContext) -> None:
    """
    Apply all migrations.

    Args:
        alembic_env: alembic environment context

    Returns:
        None
    """
    async with engine.begin() as conn:
        await conn.run_sync(do_run_migrations, alembic_env)


async def migrate(url: str) -> None:
    alembic_conf = Config()
    alembic_conf.set_main_option("script_location", "alembic")
    alembic_conf.set_main_option("url", url)
    alembic_script = ScriptDirectory.from_config(alembic_conf)
    alembic_env = EnvironmentContext(alembic_conf, alembic_script)

    await async_migrate(alembic_env)


async def disconnect() -> None:
    """
    Dispose a database engine and destroy all of its connections.

    Args:

    Returns:
        None
    """

    await engine.dispose()


# async def


# @pytest_asyncio.fixture(scope="session")
# async def engine() -> AsyncEngine:
#     """
#     Create async engine and run alembic migrations on database.
#
#     Returns:
#         sqlalchemy async engine
#     """
#     await migrate(get_sqlalchemy_db_uri())
#     yield engine
#     await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def db() -> AsyncSession:
    """
    Create async engine and run alembic migrations on database.

    Returns:
        sqlalchemy async session
    """
    await migrate(get_sqlalchemy_db_uri())
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
