"""
Auth utils.

Attrs:
    create_access_token: creates access or refresh JWT token.
    decode_token: decodes and verifies JWT token.
"""
import json
from datetime import timedelta, datetime

from jose import jwt

from app.core.config import settings


def create_access_token(subject: dict, expires_delta: timedelta = None) -> str:
    """
    Creates access/refresh JWT token.

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
    to_encode = {"exp": expire, "sub": json.dumps(subject)}
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
    jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
