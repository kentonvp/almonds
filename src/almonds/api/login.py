from flask import Blueprint, redirect, render_template, request, session, url_for
from pydantic import EmailStr
from pydantic.types import SecretStr
from werkzeug.security import generate_password_hash

from almonds.crud import user_crud
from almonds.schemas.user import UserBase
from almonds.services.login import validate_login, is_valid_password

login_bp = Blueprint("login", __name__)


@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Confirm login correct.
        if validate_login(username, password):
            session["username"] = username
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
        elif user_crud.get_user_by_username(username) is not None:
            return render_template(
                "create_user.html",
                error_msg="That username is already taken, please try another...",
            )
        else:
            user = user_crud.create_user(
                UserBase(
                    username=username,
                    password=SecretStr(generate_password_hash(password)),
                    email=email,
                )
            )

            session["username"] = username

    return redirect(url_for("root.view"))
