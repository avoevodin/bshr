"""
Pydantic User schemas.

Attrs:
    UserBase: common user properties.
    UserCreate: create user properties.
    UserUpdate: update user properties.
    UserInDBBase: common user db properties.
    User: main user properties to return via API.
    UserInDB: user properties stored in DB.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, constr, validator

from app.utils.user import validate_username


class UserBase(BaseModel):
    """
    Shared user properties.
    """

    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    confirmed: bool = False


class UserCreate(UserBase):
    """
    Properties to receive via API on create.
    """

    username: str = None
    email: EmailStr = None
    password: constr(min_length=8, max_length=200)
    is_superuser: bool = False

    @validator("username", pre=True)
    def username_is_valid(cls, username: str) -> Optional[str]:
        """
        Check username is valid.

        Args:
            username: username string

        Returns:
            username string
        """
        return validate_username(username)


class UserUpdate(UserBase):
    """
    Properties to receive via API on update.
    """

    email: EmailStr = None
    username: str = None
    password: Optional[constr(min_length=8, max_length=200)]
    is_active: bool = None


class UserInDBBase(UserBase):
    """
    Check if user in db.
    """

    id: Optional[int] = None
    created: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        """
        Config for user schema.
        """

        orm_mode = True


class User(UserInDBBase):
    """
    User properties to return via API.
    """

    pass


class UserInDB(UserInDBBase):
    """
    User properties stored in db.
    """

    hashed_password: str
