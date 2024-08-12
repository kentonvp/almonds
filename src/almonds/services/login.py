from werkzeug.security import check_password_hash, generate_password_hash

from almonds.crud import user as crud_user
from almonds.schemas.user import User


def validate_login(username: str, password: str) -> User | None:
    user = crud_user.get_user_by_username(username)
    if user is not None and check_password_hash(
        user.password.get_secret_value(), password
    ):
        return user

    return None


def is_valid_password(password: str) -> bool:
    return len(password) > 3


def hash_password(password: str) -> str:
    return generate_password_hash(password)
