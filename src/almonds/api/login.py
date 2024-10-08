from flask import Blueprint, redirect, render_template, request, session, url_for
from pydantic.types import SecretStr

from almonds.crud import user as crud_user
from almonds.schemas.user import UserBase
from almonds.services.login import hash_password, is_valid_password, validate_login

login_bp = Blueprint("login", __name__)


def store_user_session(user):
    session["username"] = user.username
    session["user_id"] = user.id


@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Confirm login correct.
        if user := validate_login(username, password):
            store_user_session(user)
        else:
            return render_template(
                "login.html", error_msg="Incorrect username or password..."
            )

    return redirect(url_for("root.view"))


@login_bp.route("/logout", methods=["GET", "POST"])
def logout():
    if request.method == "POST" and "username" in session:
        session.clear()

    return redirect(url_for("root.view"))


@login_bp.route("/createUser")
def create_user():
    return render_template("create_user.html")


@login_bp.route("/handleNewUser", methods=["GET", "POST"])
def handle_new_user():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        c_password = request.form["confirm_password"]
        email = request.form["user_email"]

        if password != c_password:
            return render_template(
                "create_user.html", error_msg="Your passwords did not match..."
            )
        elif not is_valid_password(password):
            return render_template(
                "create_user.html", error_msg="Password does not satisfy checks..."
            )
        elif crud_user.get_user_by_username(username) is not None:
            return render_template(
                "create_user.html",
                error_msg="That username is already taken, please try another...",
            )
        else:
            user = crud_user.create_user(
                UserBase(
                    username=username,
                    password=SecretStr(hash_password(password)),
                    email=email,
                )
            )
            store_user_session(user)

    return redirect(url_for("root.view"))
