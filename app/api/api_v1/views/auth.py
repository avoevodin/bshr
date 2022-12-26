"""
Authentication handlers module.
"""
import uuid
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.requests import Request

from app import schemas, crud
from app.core import security
from app.core.config import settings

router = APIRouter()


@router.post(
    "/login/access-token",
    name="login:access_token",
    summary="Login and get an access token.",
    status_code=status.HTTP_200_OK,
    description="User login view.",
    response_model=schemas.Token,
)
async def login_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    db = request.app.state.db
    username = form_data.username
    password = form_data.password

    user = crud.user.authenticate_by_email(db, username, password)
    if not user:
        user = crud.user.authenticate_by_username(db, username, password)
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

    access_token = {**token_subject, "token-type": "access_token"}
    refresh_token = {**token_subject, "token-type": "refresh_token"}
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    token = schemas.Token(
        access_token=security.create_access_token(access_token, access_token_expires),
        refresh_token=security.create_access_token(
            refresh_token, refresh_token_expires
        ),
    )
    return token
