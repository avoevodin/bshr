"""
Security utils.

Attrs:
    password_hash_ctx: context for creating password using
                       password based key derivative func 2
                       algorithm.
    get_password_hash: returns hashed password.
    verify_password: verified plain and hashed passwords.
"""

from passlib.context import CryptContext

password_hash_ctx = CryptContext(
    schemes=["pbkdf2_sha256"],
    pbkdf2_sha256__min_rounds=18000,
    pbkdf2_sha256__max_rounds=26000,
)


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
