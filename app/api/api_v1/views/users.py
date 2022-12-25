"""
Login view handlers.
"""
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from starlette.requests import Request

from app import crud, models, dependencies
from app.schemas import User, UserCreate
from app.schemas.login import Register

router = APIRouter()


@router.post(
    "/register",
    name="users:register",
    summary="Registry a new user",
    status_code=status.HTTP_200_OK,
    description="Registers new user",
    response_model=User,
)
async def user_register(register: Register, request: Request) -> Optional[User]:
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
                f"User with email (username) {register.email} ({register.username})"
                " already exists"
            ),
        )
    user_in = UserCreate.parse_obj(register)
    user_db = await crud.user.create(db, obj_in=user_in)

    return user_db


@router.get(
    "/",
    name="users:read_users",
    summary="Get users list",
    status_code=status.HTTP_200_OK,
    description="Get all users list",
    response_model=List[User],
)
async def read_users(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    current_super_user: models.User = Depends(
        dependencies.get_current_active_superuser
    ),
) -> Optional[List[models.User]]:
    """
    Get the list of all users.
    Args:
        request: request instance
        skip: number of users that should be skipped
        limit: max number of users
        current_super_user: superuser auth dependency

    Returns:
        List of users if success, None otherwise
    """
    db = request.app.state.db
    users_list = await crud.user.get_multi(db, skip=skip, limit=limit)
    return users_list
