"""
Pydantic login schemas.
"""
from typing import Optional

from pydantic import BaseModel, EmailStr, constr, validator
from utils.user import validate_username


class Register(BaseModel):
    """
    Register input scheme.
    """

    username: str = None
    email: EmailStr = None
    password: constr(min_length=8, max_length=200)

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


class Auth(Register):
    """
    Authentication input schema.
    """

    pass


class Token(BaseModel):
    """
    Token schema.
    """

    access_token: str
    refresh_token: str
    token_type: str

    class Config:
        """
        Config for token schema.
        """

        orm_mode = True


class TokenPayload(BaseModel):
    """
    Token payload schema.
    """

    sub: Optional[int] = None
