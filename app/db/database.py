from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import crud
import schemas
from core.config import settings
from utils.database import get_sqlalchemy_db_uri


async def app_init_db(app: FastAPI) -> None:
    """
    Init database function.

    :param app: FastAPI application
    :return: None
    """
    engine = create_async_engine(
        url=get_sqlalchemy_db_uri(),
        echo=False,
        pool_size=50,
        pool_pre_ping=True,
    )
    async_session = sessionmaker(
        engine, expire_on_commit=False, autoflush=False, class_=AsyncSession
    )

    session = async_session(bind=engine)
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
            passwors=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        await crud.user.create(session, user_in)


async def app_dispose_db(app: FastAPI) -> None:
    """
    Dispose db-connection.
    :param app: FastAPI application.
    :return: None
    """
    session = app.state.db
    await session.close()
