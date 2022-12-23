"""
Utils for users part of app.

Attrs:
    validate_username: Check for valid username.
"""
import string
from typing import Optional


def validate_username(username: str) -> Optional[str]:
    """
    Check for valid username
    :param username: username string
    :return:
    """
    allowed = string.ascii_letters + string.digits + "_"
    assert all(ch in allowed for ch in username), "Invalid characters in username."
    assert len(username) > 2, "Username must be 3 characters or more."
    return username
