from app.db import Base


def test_import_model_user() -> None:
    from app.models.user import User

    assert issubclass(User, Base)
    assert User.__name__.lower() == User.__tablename__
