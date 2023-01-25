"""
Common utilities for service communicates.
"""
from app import schemas


async def send_register_confirmation_message(user_in: schemas.UserCreate) -> None:
    """
    Send register confirmation message for the new user.

    Args:
        user_in: user data

    Returns:
        None
    """
    pass
