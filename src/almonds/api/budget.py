import datetime

from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from almonds.crud import budget as crud_budget
from almonds.crud import category as crud_category
from almonds.crud import transaction as crud_transaction
from almonds.templates.filters import format_currency
from almonds.utils import status_code

budget_bp = Blueprint("budget", __name__)


@budget_bp.route("/")
def view():
    if "username" not in session:
        return redirect(url_for("root.view"))

    budgets_ = crud_budget.get_budgets_by_user_id(session["user_id"])

    transactions = crud_transaction.get_transactions_by_month(session["user_id"])

    categories = {
        c.id: c.name for c in crud_category.get_categories_by_user(session["user_id"])
    }

    budgets = []
    for b in budgets_:
        # Add transaction amounts to budget
        category = categories[b.category_id]
        spent = sum(
            -transaction.amount
            for transaction in transactions
            if transaction.category_id == b.category_id
        )

        # Add percentage and status_color
        percentage = round(spent / b.amount * 100, 2)
        status_color = budget_color(percentage)

        budgets.append(
            {
                "category": category,
                "amount": b.amount,
                "spent": spent,
                "percentage": percentage,
                "status_color": status_color,
            }
        )

    categories = [{"id": cid, "name": name} for cid, name in categories.items()]

    return render_template(
        "budget.html", budgets=budgets, categories=categories, **build_context()
    )


@budget_bp.route("/create", methods=["POST"])
def create_budget():
    pass


@budget_bp.route("/lastMonthSpending", methods=["POST"])
def get_last_month_spending():
    body = request.get_json()
    if "category_id" not in body:
        return (
            jsonify({"error": "Category ID not provided"}),
            status_code.HTTP_400_BAD_REQUEST,
        )
    category_id = body["category_id"]

    dt = datetime.datetime.utcnow()
    last_month_dt = dt - datetime.timedelta(days=dt.day)
    transactions = crud_transaction.get_transactions_by_month(
        session["user_id"], last_month_dt
    )

    spent = sum(
        -transaction.amount
        for transaction in transactions
        if transaction.category_id == category_id
    )

    return jsonify({"amount": format_currency(spent)}), status_code.HTTP_200_OK


def build_context():
    return {
        "title": "Budgets",
        "user": {"username": session["username"]},
    }


def budget_color(percentage: float) -> str:
    """Return the color status of a budget based on the percentage spent."""
    if percentage > 100:
        return "danger"
    if percentage > 75:
        return "warning"
    return "success"
