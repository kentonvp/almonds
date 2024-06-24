from werkzeug.security import check_password_hash, generate_password_hash

from almonds.crud import user_crud


def validate_login(username: str, password: str) -> bool:
    user = user_crud.get_user_by_username(username)
    if user is not None:
        return check_password_hash(user.password.get_secret_value(), password)

    return False


def is_valid_password(password: str) -> bool:
    return len(password) > 3


def hash_password(password: str) -> str:
    return generate_password_hash(password)
