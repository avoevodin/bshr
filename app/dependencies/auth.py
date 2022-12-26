from typing import Optional

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from starlette import status
from starlette.requests import Request

import crud.crud_user
from app import models


async def get_current_user(request: Request, token: str = "") -> models.User:
    db = request.app.state.db
    user = await crud.user.get_by_username(db, username="test")
    return user


async def get_current_active_superuser(
    request: Request,
    current_user: models.User = Depends(get_current_user),
) -> Optional[models.User]:
    """
    Returns superuser using passed token.
    Args:
        request: request instance
        current_user: current user get by token.

    Returns:
        current user if it's a superuser, otherwise None
    """
    if not crud.crud_user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user doesn't have enough privileges.",
        )

    return current_user
