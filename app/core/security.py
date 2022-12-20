"""
Security utils.

Attrs:
    password_hash_ctx: context for creating password using
                       password based key derivative func 2
                       algorithm.
    create_access_token: creates access or refresh JWT token.
    decode_token: decodes and verifies JWT token.
    get_password_hash: returns hashed password.
    verify_password: verified plain and hashed passwords.
"""
from datetime import timedelta, datetime
from typing import Union, Any

from core.config import settings
from jose import jwt
from passlib.context import CryptContext

password_hash_ctx = CryptContext(
    schemes=["pbkdf2_sha256"],
    pbkdf2_sha256__min_rounds=18000,
    pbkdf2_sha256__max_rounds=26000,
)


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
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
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def decode_token(token: str) -> dict:
    """
    Decode and verify JWT token.

    Args:
        token: input JWT token string.

    Returns:
        dict of decoded data (key, value)
    """
    jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def get_password_hash(password: str) -> str:
    """
    Get hashed password string.

    Args:
        password: password string.

    Returns:
        hashed password string.
    """
    return password_hash_ctx.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password with its hash.

    Args:
        plain_password: plain password string.
        hashed_password: hashed password string.

    Returns:
        True if password is correct, False otherwise.
    """
    return password_hash_ctx.verify(plain_password, hashed_password)
