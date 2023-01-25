"""
Project config module.

Attrs:
    settings: instance of main Settings class.
"""
import secrets
from typing import List, Union

from pydantic import BaseSettings, AnyHttpUrl, validator


class Settings(BaseSettings):
    """
    Main class for all settings.
    """

    API_V1_STR: str = "/api/v1"
    SERVER_NAME: str = "bshr"
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

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
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

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

    REDIS_HOST: str
    REDIS_PORT: str

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
