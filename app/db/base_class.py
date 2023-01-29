"""
Declarative base for SQLAlchemy.
"""
from typing import Any

from sqlalchemy.orm import as_declarative, declared_attr


@as_declarative()
class Base:
    """
    Declarative base class for SQLAlchemy.
    """

    id: Any
    __name__: str

    # noinspection SpellCheckingInspection
    @declared_attr
    def __tablename__(cls) -> str:  # noqa
        """
        Autogenerate table name.
        """
        return cls.__name__.lower()
