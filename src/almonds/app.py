from flask import Flask

from almonds.api.home import home
from almonds.api.login import login_bp
from almonds.db.base import Base, engine


def create_app():
    Base.metadata.create_all(engine)

    app = Flask(__name__)
    app.secret_key = "YES.A.VERY.SECRET.KEY"

    app.register_blueprint(home)
    app.register_blueprint(login_bp)

    return app
