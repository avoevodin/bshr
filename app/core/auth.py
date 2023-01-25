"""
Auth utils.

Attrs:
    create_access_token: creates access or refresh JWT token.
    decode_token: decodes and verifies JWT token.
"""
import json
from datetime import timedelta, datetime

from fastapi.security import OAuth2PasswordBearer
from jose import jwt

from app import schemas
from app.core import auth
from app.core.config import settings

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}{settings.LOGIN_ACCESS_TOKEN_PATH}",
)

reusable_oauth2_refresh = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}{settings.LOGIN_REFRESH_TOKEN_PATH}",
)


def create_tokens(token_subject: dict) -> schemas.Token:
    """
    Create token object with access and refresh tokens included.

    Args:
        token_subject: subject dict to be added to tokens


    Returns:
        pydantic token object with access and refresh token.
    """
    access_token = schemas.TokenSubject.parse_obj(
        {**token_subject, "token_type": "access_token"}
    )
    refresh_token = schemas.TokenSubject.parse_obj(
        {**token_subject, "token_type": "refresh_token"}
    )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    token = schemas.Token(
        access_token=auth.create_access_token(access_token, access_token_expires),
        refresh_token=auth.create_access_token(refresh_token, refresh_token_expires),
        token_type="bearer",
    )
    return token


def create_access_token(
    subject: schemas.TokenSubject, expires_delta: timedelta = None
) -> str:
    """
    Create access/refresh JWT token.

    Args:
        subject: subject dict to be added to token
        expires_delta: token ttl, expire delta time in minutes

    Returns:
        string containing JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": json.dumps(subject.dict())}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Decode and verify JWT token.

    Args:
        token: input JWT token string.

    Returns:
        dict of decoded data (key, value)
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
