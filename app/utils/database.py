"""
Database utils.

Attrs:
    get_sqlalchemy_db_uri: returns sqlalchemy database uri using env vars.
"""
from app.core.config import settings


def get_sqlalchemy_db_uri():
    """
    Returns SQLAlchemy database uri using settings.

    Returns:
        SQLAlchemy database uri string
    """
    return (
        f"{settings.SQLALCHEMY_DATABASE_DRIVER}://"
        f"{settings.SQLALCHEMY_DATABASE_USER}:{settings.SQLALCHEMY_DATABASE_PASSWORD}"
        f"@{settings.SQLALCHEMY_DATABASE_HOST}:{settings.SQLALCHEMY_DATABASE_PORT}"
        f"/{settings.SQLALCHEMY_DATABASE_NAME}"
    )


def get_redis_db_uri():
    """
    Returns Redis database uri using settings.

    Returns:
        Redis database uri string
    """
    return f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
