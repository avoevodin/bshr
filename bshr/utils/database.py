"""
Database utils.

Attrs:
    get_db_uri: returns db uri using env vars.
"""
from core.config import settings


def get_sqlalchemy_db_uri():
    return (
        f"{settings.SQLALCHEMY_DATABASE_DRIVER}://"
        f"{settings.SQLALCHEMY_DATABASE_USER}:{settings.SQLALCHEMY_DATABASE_PASSWORD}"
        f"@{settings.SQLALCHEMY_DATABASE_HOST}:{settings.SQLALCHEMY_DATABASE_PORT}"
        f"/{settings.SQLALCHEMY_DATABASE_NAME}"
    )
