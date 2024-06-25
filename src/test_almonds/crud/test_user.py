from datetime import datetime
from uuid import uuid4

from pydantic import SecretStr

from almonds.crud import user as crud_user
from almonds.models.user import User as UserModel
from almonds.schemas.user import User, UserBase, UserUpdate


def test_create_user(sessionmaker_test):
    user_base = UserBase(
        email="test@example.com", username="testuser", password=SecretStr("password123")
    )

    created_user = crud_user.create_user(user_base, sessionmaker=sessionmaker_test)

    assert created_user.email == "test@example.com"
    assert created_user.username == "testuser"
    assert isinstance(created_user.id, uuid4().__class__)
    assert isinstance(created_user.created_at, datetime)
    assert isinstance(created_user.last_updated, datetime)


def test_get_user_by_id(sessionmaker_test):
    user_base = UserBase(
        email="test@example.com", username="testuser", password=SecretStr("password123")
    )
    created_user = crud_user.create_user(user_base, sessionmaker=sessionmaker_test)

    retrieved_user = crud_user.get_user_by_id(
        created_user.id, sessionmaker=sessionmaker_test
    )

    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.email == created_user.email
    assert retrieved_user.username == created_user.username


def test_get_user_by_username(sessionmaker_test):
    user_base = UserBase(
        email="test@example.com", username="testuser", password=SecretStr("password123")
    )
    created_user = crud_user.create_user(user_base, sessionmaker=sessionmaker_test)

    retrieved_user = crud_user.get_user_by_username(
        "testuser", sessionmaker=sessionmaker_test
    )

    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.email == created_user.email
    assert retrieved_user.username == created_user.username


def test_update_user(sessionmaker_test):
    user_base = UserBase(
        email="test@example.com", username="testuser", password=SecretStr("password123")
    )
    created_user = crud_user.create_user(user_base, sessionmaker=sessionmaker_test)

    updated_user = UserUpdate(
        id=created_user.id,
        username=created_user.username,
        email="newemail@example.com",
        password=created_user.password,
    )

    result = crud_user.update_user(updated_user, sessionmaker=sessionmaker_test)

    assert result.email == "newemail@example.com"
    assert result.last_updated > created_user.last_updated


def test_delete_user(sessionmaker_test):
    user_base = UserBase(
        email="test@example.com", username="testuser", password=SecretStr("password123")
    )
    created_user = crud_user.create_user(user_base, sessionmaker=sessionmaker_test)

    crud_user.delete_user(created_user.id, sessionmaker=sessionmaker_test)

    retrieved_user = crud_user.get_user_by_id(
        created_user.id, sessionmaker=sessionmaker_test
    )
    assert retrieved_user is None


def test_get_nonexistent_user(sessionmaker_test):
    non_existent_id = uuid4()
    retrieved_user = crud_user.get_user_by_id(
        non_existent_id, sessionmaker=sessionmaker_test
    )
    assert retrieved_user is None

    retrieved_user = crud_user.get_user_by_username(
        "nonexistentuser", sessionmaker=sessionmaker_test
    )
    assert retrieved_user is None
