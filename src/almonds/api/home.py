from flask import Blueprint, render_template, request, session

home = Blueprint("home", __name__)


def build_context(**kwargs) -> dict:
    base = {
        "title": "dashboard",
    }

    return base | kwargs


@home.route("/")
def view():
    if "username" in session:
        context = build_context(username=session["username"], loggedin=True)
        return render_template("home.html", **context)

    context = build_context()
    return render_template("login_view.html", **context)
