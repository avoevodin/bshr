"""
Pytest application configuration.

Args:

"""

from typing import List

from alembic.config import Config
from alembic.operations import Operations
from alembic.runtime.environment import EnvironmentContext
from alembic.runtime.migration import MigrationContext, RevisionStep
from alembic.script import ScriptDirectory
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.future import Connection

from app.db import Base


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
    alembic_conf = Config()
    alembic_conf.set_main_option("script_location", "alembic")
    alembic_conf.set_main_option("url", url)
    alembic_script = ScriptDirectory.from_config(alembic_conf)
    alembic_env = EnvironmentContext(alembic_conf, alembic_script)

    await async_migrate(engine, alembic_env)


async def disconnect(engine: AsyncEngine) -> None:
    """
    Dispose a database engine and destroy all of its connections.

    Args:
        engine: async sqlalchemy engine to be disposed

    Returns:
        None
    """

    await engine.dispose()
