"""
Database initialization methods.

Attrs:
    app_init_db: database initialization.
    app_dispose_db: database disposing.
"""
from fastapi import FastAPI

from app import crud, schemas
from app.core.config import settings
from app.db.session import session


async def app_init_db(app: FastAPI) -> None:
    """
    Init database function.

    Args:
        app: FastAPI application

    Returns:
        None
    """
    app.state.db = session

    if settings.FIRST_SUPERUSER_EMAIL:
        user = await crud.user.get_by_email(
            session, email=settings.FIRST_SUPERUSER_EMAIL
        )
    else:
        user = await crud.user.get_by_username(session, settings.FIRST_SUPERUSER)

    if not user:
        user_in = schemas.UserCreate(
            username=settings.FIRST_SUPERUSER,
            email=settings.FIRST_SUPERUSER_EMAIL,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        await crud.user.create(session, obj_in=user_in)


async def app_dispose_db(app: FastAPI) -> None:
    """
    Dispose db-connection.

    Args:
        app: FastAPI application.

    Returns:
        None
    """
    session = app.state.db
    await session.close()
