"""
SQLAlchemy async session initialization module.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_async_engine(
    url=settings.SQLALCHEMY_DATABASE_URI,
    echo=False,
    pool_size=50,
    pool_pre_ping=True,
    pool_recycle=300,
)
async_session = sessionmaker(
    engine, expire_on_commit=False, autoflush=False, class_=AsyncSession
)

session = async_session(bind=engine)
