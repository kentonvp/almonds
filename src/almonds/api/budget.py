import datetime
import math
from uuid import UUID

from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from almonds.api import root
from almonds.crud import budget as crud_budget
from almonds.crud import category as crud_category
from almonds.crud import transaction as crud_transaction
from almonds.schemas.budget import Budget, BudgetBase
from almonds.templates.filters import format_currency
from almonds.utils import status_code, ui

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
        status_color = ui.budget_color(percentage)

        budgets.append(
            {
                "id": b.id,
                "category": category,
                "amount": b.amount,
                "spent": spent,
                "percentage": int(math.ceil(percentage)),
                "status_color": status_color,
            }
        )

    categories = [{"id": cid, "name": name} for cid, name in categories.items()]

    return render_template(
        "budget.html", budgets=budgets, categories=categories, **build_context()
    )


@budget_bp.route("/get", methods=["POST"])
def get_budget():
    body = request.get_json()
    if "budget_id" not in body:
        return (
            jsonify({"error": "Budget ID not provided"}),
            status_code.HTTP_400_BAD_REQUEST,
        )

    budget_id = UUID(body["budget_id"])
    budget = crud_budget.get_budget(budget_id)
    category = crud_category.get_category_by_id(budget.category_id)
    if budget:
        return (
            jsonify(budget.model_dump() | {"category": category.name}),
            status_code.HTTP_200_OK,
        )

    return jsonify({"error": "Budget not found"}), status_code.HTTP_404_NOT_FOUND


@budget_bp.route("/create", methods=["POST"])
def create_budget():
    c_budget = BudgetBase(
        user_id=session["user_id"],
        category_id=int(request.form["budget-category"]),
        amount=float(request.form["budget-amount"]),
        start_date=datetime.date.today(),
    )
    crud_budget.create_budget(c_budget)
    return redirect(url_for("budget.view"))


@budget_bp.route("/update", methods=["POST"])
def update_budget():
    u_budget = Budget(
        id=UUID(request.form["budget-id"]),
        user_id=session["user_id"],
        category_id=int(request.form["budget-category-id"]),
        amount=float(request.form["budget-amount"]),
        start_date=datetime.date.today(),
    )
    crud_budget.update_budget(u_budget)
    return redirect(url_for("budget.view"))


@budget_bp.route("/delete", methods=["POST"])
def delete_budget():
    body = request.get_json()
    print(f"{body=}")
    budget_id = UUID(body["budget_id"])
    crud_budget.delete_budget(budget_id)
    return redirect(url_for("budget.view"))


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
    base = root.build_context()

    return base | {
        "title": "Budgets",
        "user": {"username": session["username"]},
    }
