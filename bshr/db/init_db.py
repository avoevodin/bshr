from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from core.config import settings


async def app_init_db(app: FastAPI) -> None:
    """
    Init database function.

    :param app: FastAPI application
    :return: None
    """
    engine = create_async_engine(
        url=settings.DATABASE_URL, echo=False, pool_size=50, pool_pre_ping=True
    )
    async_session = sessionmaker(
        engine, expire_on_commit=False, autoflush=False, class_=AsyncSession
    )

    session = async_session(bind=engine)
    app.state.db = session

    user = None
