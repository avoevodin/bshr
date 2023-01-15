from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.utils.database import get_sqlalchemy_db_uri

engine = create_async_engine(
    url=get_sqlalchemy_db_uri(),
    echo=False,
    pool_size=50,
    pool_pre_ping=True,
    pool_recycle=300,
)
async_session = sessionmaker(
    engine, expire_on_commit=False, autoflush=False, class_=AsyncSession
)

session = async_session(bind=engine)
