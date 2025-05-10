import os

from flask import Flask, request
from prometheus_flask_exporter import PrometheusMetrics

from almonds.api.budget import budget_bp
from almonds.api.goals import goal_bp
from almonds.api.login import login_bp
from almonds.api.plaid import plaid_bp
from almonds.api.root import root
from almonds.api.transactions import transaction_bp
from almonds.db.base import Base, engine
from almonds.templates.filters import format_currency, format_date, format_dollars
from almonds.utils.logging import logger
from src.almonds.utils import status_code


def create_app():
    Base.metadata.create_all(engine)

    app = Flask(__name__)

    metrics = PrometheusMetrics(app)
    logger.info("Prometheus metrics initializaed")

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
        return {
            "error": "An internal error occurred"
        }, status_code.HTTP_500_SERVER_ERROR

    @app.route("/metrics")
    def exports_metrics():
        logger.info("Serving custom metrics")
        response_data, content_type = metrics.generate_metrics(
            accept_header="application/json"
        )
        return response_data, status_code.HTTP_200_OK, {"Content-Type": content_type}

    return app
