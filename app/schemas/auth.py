"""
Pydantic login schemas.
"""
from typing import Optional, List

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


class TokenSubject(BaseModel):
    """
    Token subject schema.
    """

    id: int
    username: str
    email: str
    jti: str
    token_type: str
    scope: List[str]


class TokenPayload(BaseModel):
    """
    Token payload schema.
    """

    sub: Optional[str] = None
