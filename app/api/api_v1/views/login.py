"""
Login view handlers.
"""
from typing import Optional

from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.requests import Request

from app import crud
from app.schemas import User, UserCreate
from app.schemas.login import Register

router = APIRouter()


@router.post(
    "/login/register/",
    name="login:register",
    summary="Registry a new user",
    status_code=status.HTTP_200_OK,
    description="Registers new user",
    response_model=User,
)
async def login_register(register: Register, request: Request) -> Optional[User]:
    """
    View function for creation new unprivileged user from registration.

    Args:
        register: user data (email, username, password)
        request: request instance

    Returns:
        optionally a newly registered user from database.
    """
    db = request.app.state.db
    found_user = None

    if register.email:
        found_user = await crud.user.get_by_email(db, email=register.email)
    if not found_user and register.username:
        found_user = await crud.user.get_by_username(db, username=register.username)
    if found_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"User with email/username {register.email}/{register.username} already"
                " exists"
            ),
        )
    user_in = UserCreate.parse_obj(register)
    user_db = await crud.user.create(db, obj_in=user_in)

    return user_db
