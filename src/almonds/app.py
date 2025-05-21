import datetime
import os

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import Flask, render_template, request, session
from flask_wtf.csrf import CSRFError, CSRFProtect
from prometheus_flask_exporter import PrometheusMetrics

from almonds.api import home
from almonds.api.budget import budget_bp
from almonds.api.goals import goal_bp
from almonds.api.home import root
from almonds.api.login import login_bp
from almonds.api.plaid import plaid_bp
from almonds.api.transactions import transaction_bp
from almonds.crypto.cryptograph import Cryptograph
from almonds.db.base import Base, engine
from almonds.services import plaid_sync
from almonds.templates.filters import format_currency, format_date, format_dollars
from almonds.utils import status_code
from almonds.utils.logging import logger


def create_app():
    Base.metadata.create_all(engine)

    app = Flask(__name__)

    metrics = PrometheusMetrics(app)
    logger.info("Prometheus metrics initializaed")

    # Initialize CSRF protection
    CSRFProtect(app)
    logger.info("CSRF protection initialized")

    if os.getenv("ALMONDS_SECRET") is None:
        raise ValueError("ALMONDS_SECRET environment variable not set")

    app.secret_key = os.getenv("ALMONDS_SECRET")

    # Set the default session lifetime to 15 minutes.
    app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(minutes=15)

    app.jinja_env.filters |= {
        "format_currency": format_currency,
        "format_date": format_date,
        "format_dollars": format_dollars,
    }

    app.register_blueprint(root)
    app.register_blueprint(login_bp)
    app.register_blueprint(plaid_bp, url_prefix="/plaid")
    app.register_blueprint(transaction_bp, url_prefix="/transactions")
    app.register_blueprint(budget_bp, url_prefix="/budget")
    app.register_blueprint(goal_bp, url_prefix="/goals")

    @app.before_request
    def update_session_lifetime():
        session.permanent = True
        app.permanent_session_lifetime = datetime.timedelta(minutes=15)

    @app.before_request
    def log_request_info():
        logger.info(f"Handling request: {request.method} {request.path}")

    @app.route("/metrics")
    def exports_metrics():
        logger.info("Serving custom metrics")
        response_data, content_type = metrics.generate_metrics(
            accept_header="application/json"
        )
        return response_data, status_code.HTTP_200_OK, {"Content-Type": content_type}

    @app.errorhandler(status_code.HTTP_404_NOT_FOUND)
    def page_not_found(e):
        return (
            render_template("404.html", **home.build_context()),
            status_code.HTTP_404_NOT_FOUND,
        )

    @app.errorhandler(Exception)
    def server_error(e):
        logger.error(f"Server error: {e}", exc_info=True)
        return (
            render_template("500.html", **home.build_context()),
            status_code.HTTP_500_SERVER_ERROR,
        )

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        logger.error(f"CSRF error: {e}", exc_info=True)
        return (
            render_template("csrf_error.html", reason=e.description),
            status_code.HTTP_400_BAD_REQUEST,
        )

    return app


def task_scheduler() -> BackgroundScheduler:
    cryptograph = Cryptograph()

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=plaid_sync.sync,
        trigger=CronTrigger.from_crontab("0 */4 * * *"),
        kwargs={"cryptograph": cryptograph},
        id="plaid_sync",
        coalesce=True,
        replace_existing=True,
        next_run_time=datetime.datetime.now(),
    )

    return scheduler
