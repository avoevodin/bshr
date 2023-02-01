import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.crud.base import CRUDBase
from app.core.security import verify_password
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_email, random_lower_string


@pytest.mark.asyncio
async def test_get(db: AsyncSession, some_user_for_session: models.User) -> None:
    """
    Test get object by id crud operation.

    Args:
        db: SQLAlchemy session
        some_user_for_session: user created in db with session scope

    Returns:
        None
    """
    found_user = await CRUDBase(models.User).get(db, some_user_for_session.id)
    assert found_user == some_user_for_session


@pytest.mark.asyncio
async def test_get_multi(db: AsyncSession) -> None:
    """
    Test get list of objects crud operation.

    Args:
        db: SQLAlchemy session

    Returns:
        None
    """
    init_users_list = await CRUDBase(models.User).get_multi(db)
    check_list = []
    for i in range(3):
        check_list.append(await create_random_user(db))
    check_list.extend(init_users_list)

    new_users_list = await CRUDBase(models.User).get_multi(db)
    assert len(check_list) == len(new_users_list)

    for user in check_list:
        assert user in new_users_list


@pytest.mark.asyncio
async def test_update_obj_with_dict(
    db: AsyncSession, some_user_for_function: models.User
) -> None:
    """
    Test update obj crud operation with dict

    Args:
        db: SQLAlchemy session
        some_user_for_function: user created in db with function scope
    Returns:
        None
    """
    user_update_data = {"some_field": "some_value"}
    updated_user = await CRUDBase(models.User).update(
        db, obj_db=some_user_for_function, obj_in=user_update_data
    )
    assert updated_user.email == some_user_for_function.email
    assert updated_user.username == some_user_for_function.username
    assert updated_user.password == some_user_for_function.password
    assert updated_user.is_active == some_user_for_function.is_active
    assert updated_user.is_superuser == some_user_for_function.is_superuser


@pytest.mark.asyncio
async def test_remove_obj(
    db: AsyncSession, some_user_for_function: models.User
) -> None:
    """
    Test remove obj crud operation

    Args:
        db: SQLAlchemy session
        some_user_for_function: user created in db with function scope
    Returns:
        None
    """
    user_id = some_user_for_function.id
    await CRUDBase(models.User).remove(db, id=user_id)
    user_in_db = await CRUDBase(models.User).get(db, user_id)
    assert not user_in_db
