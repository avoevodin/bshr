import os
from unittest import mock

import pytest
from pydantic import ValidationError, BaseSettings


def test_import_config(
    settings_with_test_env: BaseSettings, settings_env_dict_function_scope: dict
) -> None:
    settings = settings_with_test_env
    assert (
        settings.SQLALCHEMY_DATABASE_DRIVER
        == settings_env_dict_function_scope["SQLALCHEMY_DATABASE_DRIVER"]
    )
    assert settings.BACKEND_CORS_ORIGINS == [
        i.strip()
        for i in settings_env_dict_function_scope["BACKEND_CORS_ORIGINS"].split(",")
    ]
    assert (
        settings.FIRST_SUPERUSER == settings_env_dict_function_scope["FIRST_SUPERUSER"]
    )
    assert (
        settings.FIRST_SUPERUSER_EMAIL
        == settings_env_dict_function_scope["FIRST_SUPERUSER_EMAIL"]
    )
    assert (
        settings.FIRST_SUPERUSER_PASSWORD
        == settings_env_dict_function_scope["FIRST_SUPERUSER_PASSWORD"]
    )
    assert settings.REDIS_HOST == settings_env_dict_function_scope["REDIS_HOST"]
    assert settings.REDIS_PORT == settings_env_dict_function_scope["REDIS_PORT"]
    assert (
        settings.SQLALCHEMY_DATABASE_NAME
        == settings_env_dict_function_scope["SQLALCHEMY_DATABASE_NAME"]
    )
    assert (
        settings.SQLALCHEMY_DATABASE_USER
        == settings_env_dict_function_scope["SQLALCHEMY_DATABASE_USER"]
    )
    assert (
        settings.SQLALCHEMY_DATABASE_PASSWORD
        == settings_env_dict_function_scope["SQLALCHEMY_DATABASE_PASSWORD"]
    )
    assert (
        settings.SQLALCHEMY_DATABASE_HOST
        == settings_env_dict_function_scope["SQLALCHEMY_DATABASE_HOST"]
    )
    assert (
        settings.SQLALCHEMY_DATABASE_PORT
        == settings_env_dict_function_scope["SQLALCHEMY_DATABASE_PORT"]
    )


def test_db_url(
    settings_with_test_env: BaseSettings, settings_env_dict_function_scope: dict
) -> None:
    settings = settings_with_test_env
    assert (
        settings.SQLALCHEMY_DATABASE_URI
        == "postgresql+asyncpg://user:secret@host:5432/test_db"
    )


def test_redis_url(
    settings_with_test_env: BaseSettings, settings_env_dict_function_scope: dict
) -> None:
    settings = settings_with_test_env
    assert settings.REDIS_DATABASE_URI == "redis://localhost:6379/0"


def test_import_config_with_cors_backend_list(
    settings_env_dict_function_scope: dict,
) -> None:
    BACKEND_CORS_ORIGINS_LIST = (
        "['http://localhost','http://localhost:4200','http://localhost:3000']"
    )
    settings_env_dict_function_scope["BACKEND_CORS_ORIGINS"] = BACKEND_CORS_ORIGINS_LIST
    with mock.patch.dict(os.environ, settings_env_dict_function_scope):
        from app.core.config import Settings

        settings = Settings()
        assert settings.BACKEND_CORS_ORIGINS == BACKEND_CORS_ORIGINS_LIST


def test_import_config_with_invalid_cors_backend(
    settings_env_dict_function_scope,
) -> None:
    BACKEND_CORS_ORIGINS_LIST = "invalid_string"
    settings_env_dict_function_scope["BACKEND_CORS_ORIGINS"] = BACKEND_CORS_ORIGINS_LIST
    with mock.patch.dict(os.environ, settings_env_dict_function_scope):
        from app.core.config import Settings

        with pytest.raises(ValidationError) as e:
            settings = Settings()


def test_database_uri_set_directly(settings_env_dict_function_scope) -> None:
    settings_env_dict_function_scope[
        "SQLALCHEMY_DATABASE_URI"
    ] = "postgresql://test:password@example:54321/mock_db"
    settings_env_dict_function_scope["REDIS_DATABASE_URI"] = "rediss://0.0.0.0:63791/1"
    with mock.patch.dict(os.environ, settings_env_dict_function_scope):
        from app.core.config import Settings

        settings = Settings()
        assert (
            settings.SQLALCHEMY_DATABASE_URI
            == settings_env_dict_function_scope["SQLALCHEMY_DATABASE_URI"]
        )
        assert (
            settings.REDIS_DATABASE_URI
            == settings_env_dict_function_scope["REDIS_DATABASE_URI"]
        )
        settings = None
