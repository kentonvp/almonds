from flask import Blueprint, redirect, render_template, request, session, url_for
from pydantic import EmailStr
from pydantic.types import SecretStr
from almonds.schemas.user import UserBase
from almonds.crud import user_crud

from almonds.services.login import validate_login

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
            return render_template("login_view.html", error_msg="Incorrect username or password...")

    return redirect(url_for("home.view"))


@login_bp.route("/logout", methods=["GET", "POST"])
def logout():
    if request.method == "POST":
        if 'username' in session:
            session.pop("username")

    return redirect(url_for("home.view"))


@login_bp.route("/createUser")
def create_user():
    return render_template("create_user_view.html")


@login_bp.route("/handleNewUser", methods=["GET", "POST"])
def handle_new_user():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        c_password = request.form["confirm_password"]
        email = request.form["user_email"]

        if password != c_password:
            render_template("create_user_view.html", error_msg="Passwords did not match...")
        if user_crud.get_user_by_username(username) is not None:
            render_template("create_user_view.html", error_msg="Username must be unique...")
        else:
            user = user_crud.create_user(UserBase(
                username=username,
                password=SecretStr(password),
                email=email
            ))

            session["username"] = username

    return redirect(url_for("home.view"))
