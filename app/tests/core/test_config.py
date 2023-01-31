import os
from unittest import mock

import pytest
from pydantic import ValidationError


def test_import_config(test_settings_env_dict_function_scope: dict) -> None:
    with mock.patch.dict(os.environ, test_settings_env_dict_function_scope):
        from app.core.config import settings

        assert (
            settings.SQLALCHEMY_DATABASE_DRIVER
            == test_settings_env_dict_function_scope["SQLALCHEMY_DATABASE_DRIVER"]
        )
        assert settings.BACKEND_CORS_ORIGINS == [
            i.strip()
            for i in test_settings_env_dict_function_scope[
                "BACKEND_CORS_ORIGINS"
            ].split(",")
        ]
        assert (
            settings.FIRST_SUPERUSER
            == test_settings_env_dict_function_scope["FIRST_SUPERUSER"]
        )
        assert (
            settings.FIRST_SUPERUSER_EMAIL
            == test_settings_env_dict_function_scope["FIRST_SUPERUSER_EMAIL"]
        )
        assert (
            settings.FIRST_SUPERUSER_PASSWORD
            == test_settings_env_dict_function_scope["FIRST_SUPERUSER_PASSWORD"]
        )
        assert (
            settings.REDIS_HOST == test_settings_env_dict_function_scope["REDIS_HOST"]
        )
        assert (
            settings.REDIS_PORT == test_settings_env_dict_function_scope["REDIS_PORT"]
        )
        assert (
            settings.SQLALCHEMY_DATABASE_NAME
            == test_settings_env_dict_function_scope["SQLALCHEMY_DATABASE_NAME"]
        )
        assert (
            settings.SQLALCHEMY_DATABASE_USER
            == test_settings_env_dict_function_scope["SQLALCHEMY_DATABASE_USER"]
        )
        assert (
            settings.SQLALCHEMY_DATABASE_PASSWORD
            == test_settings_env_dict_function_scope["SQLALCHEMY_DATABASE_PASSWORD"]
        )
        assert (
            settings.SQLALCHEMY_DATABASE_HOST
            == test_settings_env_dict_function_scope["SQLALCHEMY_DATABASE_HOST"]
        )
        assert (
            settings.SQLALCHEMY_DATABASE_PORT
            == test_settings_env_dict_function_scope["SQLALCHEMY_DATABASE_PORT"]
        )


def test_db_url(test_settings_env_dict_function_scope: dict) -> None:
    with mock.patch.dict(os.environ, test_settings_env_dict_function_scope):
        from app.core.config import settings

        assert (
            settings.SQLALCHEMY_DATABASE_URI
            == "postgresql+asyncpg://user:secret@host:5432/test_db"
        )


def test_redis_url(test_settings_env_dict_function_scope: dict) -> None:
    with mock.patch.dict(os.environ, test_settings_env_dict_function_scope):
        from app.core.config import settings

        assert settings.REDIS_DATABASE_URI == "redis://localhost:6379/0"


def test_import_config_with_cors_backend_list(
    test_settings_env_dict_function_scope: dict,
) -> None:
    BACKEND_CORS_ORIGINS_LIST = (
        "['http://localhost','http://localhost:4200','http://localhost:3000']"
    )
    test_settings_env_dict_function_scope[
        "BACKEND_CORS_ORIGINS"
    ] = BACKEND_CORS_ORIGINS_LIST
    with mock.patch.dict(os.environ, test_settings_env_dict_function_scope):
        from app.core.config import Settings

        settings = Settings()
        assert settings.BACKEND_CORS_ORIGINS == BACKEND_CORS_ORIGINS_LIST


def test_import_config_with_invalid_cors_backend(
    test_settings_env_dict_function_scope: dict,
) -> None:
    BACKEND_CORS_ORIGINS_LIST = "invalid_string"
    test_settings_env_dict_function_scope[
        "BACKEND_CORS_ORIGINS"
    ] = BACKEND_CORS_ORIGINS_LIST
    with mock.patch.dict(os.environ, test_settings_env_dict_function_scope):
        from app.core.config import Settings

        with pytest.raises(ValidationError) as e:
            settings = Settings()


def test_database_uri_set_directly(test_settings_env_dict_function_scope: dict) -> None:
    test_settings_env_dict_function_scope[
        "SQLALCHEMY_DATABASE_URI"
    ] = "postgresql://test:password@example:54321/mock_db"
    test_settings_env_dict_function_scope[
        "REDIS_DATABASE_URI"
    ] = "rediss://0.0.0.0:63791/1"
    with mock.patch.dict(os.environ, test_settings_env_dict_function_scope):
        from app.core.config import Settings

        settings = Settings()
        assert (
            settings.SQLALCHEMY_DATABASE_URI
            == test_settings_env_dict_function_scope["SQLALCHEMY_DATABASE_URI"]
        )
        assert (
            settings.REDIS_DATABASE_URI
            == test_settings_env_dict_function_scope["REDIS_DATABASE_URI"]
        )
