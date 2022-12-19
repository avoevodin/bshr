"""
Utils for users part of app.
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
    r = all(ch in allowed for ch in username)
    assert all(ch in allowed for ch in username), "Invalid characters in username."
    assert len(username) > 2, "Username must be 3 characters or more."
    return username
