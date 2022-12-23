"""
Database utils.

Attrs:
    get_sqlalchemy_db_uri: returns sqlalchemy database uri using env vars.
"""
from app.core.config import settings


def get_sqlalchemy_db_uri():
    """
    Returns sqlalchemy database uri using env vars.
    Returns:
        SQLAlchemy database uri string
    """
    return (
        f"{settings.SQLALCHEMY_DATABASE_DRIVER}://"
        f"{settings.SQLALCHEMY_DATABASE_USER}:{settings.SQLALCHEMY_DATABASE_PASSWORD}"
        f"@{settings.SQLALCHEMY_DATABASE_HOST}:{settings.SQLALCHEMY_DATABASE_PORT}"
        f"/{settings.SQLALCHEMY_DATABASE_NAME}"
    )
