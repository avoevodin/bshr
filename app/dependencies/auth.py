"""
Auth dependencies module.
"""
import json
from typing import Optional

from fastapi import HTTPException, Depends
from jose import jwt
from pydantic import ValidationError
from starlette import status
from starlette.requests import Request

from app import models, crud, schemas
from app.core.auth import reusable_oauth2
from app.core.config import settings


async def get_current_user(
    request: Request, token: str = Depends(reusable_oauth2)
) -> Optional[models.User]:
    """
    Return current user using token.

    Args:
        request: request instance
        token: jwt token

    Returns:
        User model instance if token is valid, None otherwise
    """
    db = request.app.state.db
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Could not validate credentials:\n{e}",
        )
    token_subject = schemas.TokenSubject.parse_obj(json.loads(token_data.sub))
    user = await crud.user.get(db, id=int(token_subject.id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User hasn't been found."
        )
    return user


async def get_current_active_user(
    request: Request,
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Return current active user using passed token.

    Args:
        request: request instance
        current_user: current user get by token.

    Returns:
        current user if it's active, otherwise None
    """
    if not crud.user.is_active(current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user."
        )
    return current_user


async def get_current_active_superuser(
    request: Request,
    current_user: models.User = Depends(get_current_active_user),
) -> Optional[models.User]:
    """
    Return superuser using passed token.

    Args:
        request: request instance
        current_user: current user get by token.

    Returns:
        current user if it's a superuser, otherwise None
    """
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user doesn't have enough privileges.",
        )

    return current_user
