import os

from flask import Flask, request

from almonds.api.budget import budget_bp
from almonds.api.goals import goal_bp
from almonds.api.login import login_bp
from almonds.api.plaid import plaid_bp
from almonds.api.root import root
from almonds.api.transactions import transaction_bp
from almonds.db.base import Base, engine
from almonds.templates.filters import format_currency, format_date, format_dollars
from almonds.utils.logging import logger


def create_app():
    Base.metadata.create_all(engine)

    app = Flask(__name__)

    if os.getenv("ALMONDS_SECRET") is None:
        raise ValueError("ALMONDS_SECRET environment variable not set")

    app.secret_key = os.getenv("ALMONDS_SECRET")

    app.jinja_env.filters["format_currency"] = format_currency
    app.jinja_env.filters["format_date"] = format_date
    app.jinja_env.filters["format_dollars"] = format_dollars

    app.register_blueprint(root)
    app.register_blueprint(login_bp)
    app.register_blueprint(plaid_bp, url_prefix="/plaid")
    app.register_blueprint(transaction_bp, url_prefix="/transactions")
    app.register_blueprint(budget_bp, url_prefix="/budget")
    app.register_blueprint(goal_bp, url_prefix="/goals")

    @app.before_request
    def log_request_info():
        logger.info(f"Handling request: {request.method} {request.path}")

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"An error occurred: {e}", exc_info=True)
        return {"error": "An internal error occurred"}, 500

    return app
