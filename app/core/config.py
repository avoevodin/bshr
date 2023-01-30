"""
Project config module.

Attrs:
    settings: instance of main Settings class.
"""
import secrets
from typing import List, Union, Optional, Dict, Any

from pydantic import BaseSettings, AnyHttpUrl, validator, PostgresDsn, RedisDsn


class Settings(BaseSettings):
    """
    Main class for all settings.
    """

    API_V1_STR: str = "/api/v1"
    SERVER_NAME: str = "bshr"
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    BACKEND_CORS_ORIGINS: Union[str, List[AnyHttpUrl]] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[str, List[str]]:
        """
        Validate and assemble cors origins for BACKEND_CORS_ORIGINS setting.

        Args:
            v: list of cors origins.

        Returns:
            validated list of cors origins if it's valid, otherwise None.
        """
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        else:
            return v

    class Config:
        """
        Nested config class.
        """

        case_sensitive = True

    PROJECT_NAME: str = "Bashare"

    SQLALCHEMY_DATABASE_DRIVER: str
    SQLALCHEMY_DATABASE_NAME: str
    SQLALCHEMY_DATABASE_USER: str
    SQLALCHEMY_DATABASE_PASSWORD: str
    SQLALCHEMY_DATABASE_HOST: str
    SQLALCHEMY_DATABASE_PORT: str

    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Optional[str]:
        """
        Validate and assemble SQLAlchemy db uri with passed settings.

        Args:
            v: current value of db uri
            values: filled settings values

        Returns:
            Database connection uri if all parameters are valid, otherwise None.
        """
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme=values.get("SQLALCHEMY_DATABASE_DRIVER"),
            user=values.get("SQLALCHEMY_DATABASE_USER"),
            password=values.get("SQLALCHEMY_DATABASE_PASSWORD"),
            host=values.get("SQLALCHEMY_DATABASE_HOST"),
            port=values.get("SQLALCHEMY_DATABASE_PORT"),
            path=f"/{values.get('SQLALCHEMY_DATABASE_NAME') or ''}",
        )

    REDIS_HOST: str
    REDIS_PORT: str

    REDIS_DATABASE_URI: Optional[RedisDsn] = None

    @validator("REDIS_DATABASE_URI", pre=True)
    def assemble_redis_connection(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Optional[str]:
        """
        Validate and assemble Rsedis db uri with passed settings.

        Args:
            v: current value of db uri
            values: filled settings values

        Returns:
            Database connection uri if all parameters are valid, otherwise None.
        """
        if isinstance(v, str):
            return v
        return RedisDsn.build(
            scheme="redis",
            host=values.get("REDIS_HOST"),
            port=values.get("REDIS_PORT"),
        )

    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_EMAIL: str
    FIRST_SUPERUSER_PASSWORD: str

    SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5
    # 8 days by default
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    LOGIN_ACCESS_TOKEN_PATH: str = "/auth/token"
    LOGIN_REFRESH_TOKEN_PATH: str = "/auth/token/refresh"


settings = Settings()
