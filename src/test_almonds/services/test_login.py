from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import SecretStr
from werkzeug.security import check_password_hash

from almonds.crud import user as crud_user
from almonds.schemas.user import User
from almonds.services.login import hash_password, is_valid_password, validate_login


@pytest.fixture(scope="function")
def mock_user():
    return User(
        id=uuid4(),
        email="test@example.com",
        username="testuser",
        password=SecretStr(hash_password("correctpassword")),
        created_at=datetime.strptime("2023-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S"),
        last_updated=datetime.strptime("2023-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S"),
    )


# Mock the crud_user.get_user_by_username function
@pytest.fixture
def mock_get_user_by_username(monkeypatch, mock_user):
    def mock_get_user(username):
        return mock_user if username == mock_user.username else None

    monkeypatch.setattr(crud_user, "get_user_by_username", mock_get_user)


def test_validate_login_success(mock_get_user_by_username, mock_user):
    assert validate_login(mock_user.username, "correctpassword") is not None


def test_validate_login_wrong_password(mock_get_user_by_username, mock_user):
    assert validate_login(mock_user.username, "wrongpassword") is None


def test_validate_login_nonexistent_user(mock_get_user_by_username):
    assert validate_login("nonexistentuser", "anypassword") is None


def test_is_valid_password():
    assert is_valid_password("validpass")
    assert not is_valid_password("123")
    assert not is_valid_password("")


def test_hash_password():
    password = "testpassword"
    hashed = hash_password(password)
    assert hashed != password
    assert len(hashed) > len(password)

    assert check_password_hash(hashed, password)
