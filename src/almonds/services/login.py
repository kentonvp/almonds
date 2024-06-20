from almonds.crud import user_crud


def validate_login(username: str, password: str) -> bool:
    user = user_crud.get_user_by_username(username)
    if user is not None:
        return user.password.get_secret_value() == password

    return False
