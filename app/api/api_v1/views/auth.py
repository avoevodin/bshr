"""
Authentication handlers module.
"""
import uuid
from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.requests import Request

from app import schemas, crud
from app.core import auth
from app.core.config import settings
from app.db.redis import set_redis_key, get_redis_key

router = APIRouter()


@router.post(
    "/token",
    name="auth:token",
    summary="Login and get an access token.",
    status_code=status.HTTP_200_OK,
    description="User login view.",
    response_model=schemas.Token,
)
async def login_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Optional[schemas.Token]:
    """
    OAuth2 compatible token login, get an access token for future requests.

    Args:
        request: request instance
        form_data: oauth2 form data

    Returns:
        token data using token schema with refresh and access token if success,
        None otherwise.
    """
    db = request.app.state.db
    username = form_data.username
    password = form_data.password

    user = await crud.user.authenticate_by_email(db, email=username, password=password)
    if not user:
        user = await crud.user.authenticate_by_username(
            db, username=username, password=password
        )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password.",
        )
    elif not crud.user.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user."
        )

    token_subject = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "jti": uuid.uuid4().hex,
    }
    if crud.user.is_superuser(user):
        token_subject.update({"scope": ["admin"]})

    access_token = {**token_subject, "token_type": "access_token"}
    refresh_token = {**token_subject, "token_type": "refresh_token"}
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    token = schemas.Token(
        access_token=auth.create_access_token(access_token, access_token_expires),
        refresh_token=auth.create_access_token(refresh_token, refresh_token_expires),
        token_type="bearer",
    )
    await set_redis_key(
        request.app.state.redis, token.refresh_token, "1", refresh_token_expires
    )
    return token


@router.post(
    "/token/refresh",
    name="auth:token-refresh",
    summary="Login and get an access token.",
    status_code=status.HTTP_200_OK,
    description="User login view.",
    response_model=schemas.Token,
)
async def login_refresh_token(
    request: Request, token: str = Depends(auth.reusable_oauth2_refresh)
) -> Optional[schemas.Token]:
    """
    OAuth2 compatible token login, get new access token and refresh token
    using passed refresh token.

    Args:
        request: request instance
        form_data: oauth2 form data

    Returns:
        token data using token schema with refresh and access token if success,
        None otherwise.
    """
    redis = request.app.state.redis
    try:
        res = await get_redis_key(redis, token)
        if res:
            print("creating token")
    except Exception as e:
        print(e)
    print(res)
