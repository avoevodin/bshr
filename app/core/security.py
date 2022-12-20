"""
Security utils.

Attrs:
    password_hash_ctx: context for creating password using
                       password based key derivative func 2
                       algorithm.
"""

from passlib.context import CryptContext

password_hash_ctx = CryptContext(
    schemes=["pbkdf2_sha256"],
    pbkdf2_sha256__min_rounds=18000,
    pbkdf2_sha256__max_rounds=26000,
)
