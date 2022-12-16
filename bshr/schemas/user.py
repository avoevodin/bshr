from typing import Optional

from pydantic import BaseModel, EmailStr, constr, validator

from utils.user import validate_username


class UserBase(BaseModel):
    """
    Shared user properties
    """

    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False


class UserCreate(UserBase):
    """
    Properties to receive via API on create.
    """

    username: str = None
    email: EmailStr = None
    password: constr(min_length=8, max_length=200)

    @validator("username", pre=True)
    def username_is_valid(cls, username: str) -> Optional[str]:
        """
        Check username is valid.
        :param username: username string
        :return: username
        """
        return validate_username(username)


class UserUpdate(UserBase):
    """
    Properties to receive via API on update.
    """

    email: EmailStr = None
    password: Optional[constr(min_length=8, max_length=200)]


class UserInDBBase(UserBase):
    """
    Check if user in db.
    """

    id: Optional[int] = None

    class Config:
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
