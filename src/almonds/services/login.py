from almonds.crud import user_crud
from werkzeug.security import check_password_hash


def validate_login(username: str, password: str) -> bool:
    user = user_crud.get_user_by_username(username)
    if user is not None:
        return check_password_hash(user.password.get_secret_value(), password)

    return False


def is_valid_password(password: str) -> bool:
    # Add password checks...
    return len(password) > 3
