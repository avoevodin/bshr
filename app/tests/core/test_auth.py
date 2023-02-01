from datetime import timedelta, datetime, timezone
import importlib
import json
import os
from uuid import uuid4

from unittest import mock

from app.schemas import TokenSubject
from app.tests.utils.utils import random_lower_string, random_email


def test_create_access_token(settings_env_dict_function_scope) -> None:
    settings_env_dict_function_scope["ACCESS_TOKEN_EXPIRE_MINUTES"] = "5"
    with mock.patch.dict(os.environ, settings_env_dict_function_scope):
        from app.core.config import settings
        from app.core.auth import create_access_token, decode_token

        token_subject_dict = {
            "id": 1,
            "username": random_lower_string(8),
            "email": random_email(),
            "jti": uuid4().hex,
            "token_type": "bearer",
            "scope": ["admin"],
        }
        token_subject = TokenSubject(**token_subject_dict)
        token = create_access_token(token_subject)
        decoded_token = decode_token(token)
        decoded_token_sub = json.loads(decoded_token["sub"])
        date_start = datetime.now(timezone.utc)
        expire_date = datetime.fromtimestamp(decoded_token["exp"], tz=timezone.utc)
        assert token_subject_dict == decoded_token_sub
        assert expire_date > date_start
        assert expire_date <= date_start + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )


def test_create_access_token_with_expires_data(
    settings_env_dict_function_scope,
) -> None:
    settings_env_dict_function_scope["ACCESS_TOKEN_EXPIRE_MINUTES"] = "5"
    with mock.patch.dict(os.environ, settings_env_dict_function_scope):
        from app.core.config import settings
        from app.core.auth import create_access_token, decode_token

        token_subject_dict = {
            "id": 1,
            "username": random_lower_string(8),
            "email": random_email(),
            "jti": uuid4().hex,
            "token_type": "bearer",
            "scope": ["admin"],
        }
        custom_expires_delta_in_minutes = 3
        token_subject = TokenSubject(**token_subject_dict)
        token = create_access_token(
            token_subject,
            expires_delta=timedelta(minutes=custom_expires_delta_in_minutes),
        )

        decoded_token = decode_token(token)
        decoded_token_sub = json.loads(decoded_token["sub"])
        date_start = datetime.now(timezone.utc)
        expire_date = datetime.fromtimestamp(decoded_token["exp"], tz=timezone.utc)
        assert token_subject_dict == decoded_token_sub
        assert expire_date > date_start
        assert expire_date <= date_start + timedelta(
            minutes=custom_expires_delta_in_minutes
        )


def test_create_tokens(settings_env_dict_function_scope) -> None:
    with mock.patch.dict(os.environ, settings_env_dict_function_scope):
        from app.core.config import settings
        from app.core.auth import create_tokens

        token_subject_dict = {
            "id": 1,
            "username": random_lower_string(8),
            "email": random_email(),
            "jti": uuid4().hex,
            "token_type": "bearer",
            "scope": ["admin"],
        }
        token = create_tokens(token_subject_dict)
        access_token = token.access_token
        refresh_token = token.refresh_token
        assert access_token
        assert refresh_token
        assert token.token_type == token_subject_dict["token_type"]
