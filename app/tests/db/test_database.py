import os
from unittest import mock

import pytest
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_init_db_without_first_user_email(
    settings_env_dict_function_scope: dict,
) -> None:
    settings_env_dict_function_scope["FIRST_SUPERUSER_EMAIL"] = ""
    with mock.patch.dict(os.environ, settings_env_dict_function_scope):
        import app.db.database
        from app.core.config import Settings

        settings = Settings()

        with mock.patch.object(app.db.database, "settings", settings):
            from app.db.database import app_init_db

            app = FastAPI()
            await app_init_db(app)
            assert isinstance(app.state.db, AsyncSession)
