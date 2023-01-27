"""
Login view handlers.
"""
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from starlette.requests import Request

from app import crud, models, dependencies, schemas

router = APIRouter()


@router.post(
    "/register",
    name="users:register",
    summary="Registry a new user",
    status_code=status.HTTP_200_OK,
    description="Registers new user",
    response_model=schemas.User,
)
async def user_register(
    user_in: schemas.UserCreate, request: Request
) -> Optional[schemas.User]:
    """
    Create a new user.

    Args:
        register: user data (email, username, password)
        request: request instance

    Returns:
        optionally a newly registered user from database.
    """
    db = request.app.state.db
    found_user = None

    if user_in.email:
        found_user = await crud.user.get_by_email(db, email=user_in.email)
    if not found_user and user_in.username:
        found_user = await crud.user.get_by_username(db, username=user_in.username)
    if found_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"User with email (username) {user_in.email} ({user_in.username})"
                " already exists"
            ),
        )
    user_db = await crud.user.create(db, obj_in=user_in)

    return user_db


@router.get(
    "/",
    name="users:read_users",
    summary="Get users list",
    status_code=status.HTTP_200_OK,
    description="Get all users list",
    response_model=List[schemas.User],
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
    Get list of all users.

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


@router.get(
    "/me",
    name="users:me",
    summary="Get current active user",
    status_code=status.HTTP_200_OK,
    description="Get current user if it's active",
    response_model=schemas.User,
)
async def get_user_me(
    current_user: schemas.User = Depends(dependencies.get_current_active_user),
) -> models.User:
    """
    Return current user by token if it's active.

    Args:
        current_user: current user get by token.

    Returns:
        current user by token if it's active, None otherwise.
    """
    return current_user


@router.patch(
    "/{user_id}",
    name="users:update",
    summary="Update user",
    status_code=status.HTTP_200_OK,
    description="Update selected user",
    response_model=schemas.User,
)
async def user_update(
    user_id: int,
    user_in: schemas.UserUpdate,
    request: Request,
    current_user: schemas.User = Depends(dependencies.get_current_active_user),
) -> Optional[schemas.User]:
    """
    Update selected user.

    Args:
        user_id: user id
        user_in: user data (email, username or password)
        request: request instance
    Returns:
        optionally an updated user from database.
    """
    db = request.app.state.db
    found_user = await crud.user.get(db, user_id)

    if not found_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id <{user_id}> not found",
        )

    if found_user != current_user and not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges.",
        )

    user_db = await crud.user.update(db, obj_db=found_user, obj_in=user_in)
    return user_db
