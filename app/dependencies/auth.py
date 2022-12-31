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
) -> models.User:
    db = request.app.state.db
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials.",
        )
    token_subject = schemas.TokenSubject.parse_obj(json.loads(token_data.sub))
    user = await crud.user.get(db, id=int(token_subject.id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User hasn't been found."
        )
    return user


async def get_current_active_superuser(
    request: Request,
    current_user: models.User = Depends(get_current_user),
) -> Optional[models.User]:
    """
    Returns active user using passed token.
    Args:
        request: request instance
        current_user: current user get by token.

    Returns:
        current user if it's active, otherwise None
    """
    if not crud.user.is_active(current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user is inactive.",
        )

    return current_user


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
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user doesn't have enough privileges.",
        )

    return current_user
