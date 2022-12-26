"""
Pydantic login schemas.
"""
from typing import Optional

from pydantic import BaseModel, EmailStr


class Register(BaseModel):
    """
    Register input scheme.
    """

    username: str
    email: EmailStr
    password: str


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
