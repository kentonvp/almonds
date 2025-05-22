import datetime
import heapq
import math

from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

import almonds.crud.budget as crud_budget
import almonds.crud.category as crud_category
import almonds.crud.goal as crud_goal
import almonds.crud.plaid.plaid_item as crud_plaid_item
import almonds.crud.transaction as crud_transaction
import almonds.crud.user_settings as crud_user_settings
import almonds.services.plaid.core as plaid_core
from almonds.crypto.cryptograph import Cryptograph
from almonds.services import charts
from almonds.utils import status_code, ui

root = Blueprint("root", __name__)


@root.route("/")
def view():
    if "username" not in session:
        context = build_context()
        return render_template("landing_page.html", **context)

    context = build_context(
        current_page="root",
    )

    context |= user_context()
    context |= top_expenses()
    context |= recent_transactions()
    context |= budget_status()
    context |= saving_goals()
    context |= available_history()
    context |= chart()
    context |= user_notifications()

    return render_template("home.html", **context)


@root.route("/settings")
def settings():
    if "username" not in session:
        return redirect(url_for("root.view"))

    # Decrypt.
    crypto = Cryptograph()

    items = crud_plaid_item.get_active_items_for_user(session["user_id"])
    updated_items = []
    for it in items:
        item_info = plaid_core.get_item_info(
            session["user_id"], crypto.decrypt(it.access_token)
        )
        updated_items.append(
            it.model_dump(
                include={
                    "id",
                    "created_at",
                    "synced_at",
                }
            )
            | {
                "institution_name": item_info["institution_name"],
                "products": item_info["products"],
            }
        )

    context = build_context(current_page="settings", plaid_items=updated_items)
    return render_template("settings.html", **context)


@root.route("/plaidLogin")
def plaid_login():
    return render_template("plaid.html", **build_context())


@root.route("/oauth")
def oauth_login():
    return render_template("oauth.html", **build_context())


@root.route("/setActiveMonth", methods=["POST"])
def set_active_month():
    data = request.get_json()
    month = data.get("month")

    if not month:
        return jsonify({"error": "Month is required."}), 400

    session["active_month"] = datetime.date(
        int(month.split("-")[0]), int(month.split("-")[1]), 1
    ).isoformat()
    return jsonify({"message": f"Active month set to {month} in session."}), 200


@root.route("/setActiveChart", methods=["POST"])
def set_active_chart():
    data = request.get_json()
    chart_type = data.get("chart")

    if not chart_type:
        return (
            jsonify({"error": "Chart is required."}),
            status_code.HTTP_400_BAD_REQUEST,
        )

    session["active_chart"] = chart_type
    return (
        jsonify({"message": f"Active chart set to {chart_type} in session."}),
        status_code.HTTP_200_OK,
    )


@root.route("/setExpectedIncome", methods=["POST"])
def set_expected_income():
    expected_income = float(request.form["expected-income-amount"])

    crud_user_settings.update_user_settings(
        session["user_id"],
        {"expected_income": expected_income},
    )
    return redirect(url_for("root.view"))


@root.route("/setTheme", methods=["POST"])
def set_theme():
    data = request.get_json()
    theme = data.get("theme")

    # validate theme
    if theme not in ("light", "dark"):
        return (
            jsonify({"error": "Theme must be either 'light' or 'dark'."}),
            status_code.HTTP_400_BAD_REQUEST,
        )

    session["theme"] = theme

    if "user_id" in session:
        crud_user_settings.update_user_settings(
            session["user_id"],
            {"theme": theme},
        )
    return (
        jsonify({"message": f"Theme set to {theme} in session."}),
        status_code.HTTP_200_OK,
    )


# Helper functions ////////////////////////////////////////////////////////////
def build_context(**kwargs) -> dict:
    base = {"title": "Dashboard", "theme": get_theme()}

    if "user_id" in session:
        base["user"] = {"username": session["username"]}

    return base | kwargs


def get_active_date() -> datetime.date:
    if "active_month" not in session:
        return datetime.date.today()

    return datetime.datetime.fromisoformat(session["active_month"])


def get_active_chart() -> str:
    return session.get("active_chart", "category")


def get_theme() -> str:
    if "user_id" in session:
        user_settings = crud_user_settings.get_user_settings(session["user_id"])
        if user_settings:
            return user_settings.get("theme", "light")

    return session.get("theme", "light")


def user_context() -> dict:
    """Returns a dictionary with the following structure:
    user: {
        username (string)
        total_balance (float)
        income_this_month (float)
        expenses_this_month (float)
        savings_goal_progress (float)
        last_month_savings (float)
        settings: (dict)
    }
    """
    transactions = crud_transaction.get_transactions_by_month(
        session["user_id"], get_active_date()
    )

    income = 0.0
    expense = 0.0

    for txn in transactions:
        if txn.amount > 0:
            income += txn.amount
        else:
            expense += txn.amount

    savings = 0 if income == 0 else (income + expense) / income * 100

    prev_transactions = crud_transaction.get_transactions_by_month(
        session["user_id"],
        datetime.date.today() - datetime.timedelta(days=datetime.date.today().day),
    )
    prev_income = 0.0
    prev_expense = 0.0
    for txn in prev_transactions:
        if txn.amount > 0:
            prev_income += txn.amount
        else:
            prev_expense += txn.amount
    prev_savings = (
        0 if prev_income == 0 else (prev_income + prev_expense) / prev_income * 100
    )

    return {
        "user": {
            "username": session["username"],
            "total_balance": income + expense,
            "income_this_month": income,
            "expenses_this_month": abs(expense),
            "savings_goal_progress": savings,
            "last_month_savings": (prev_income + prev_expense),
            "last_month_savings_change": prev_savings,
            "settings": crud_user_settings.get_user_settings(session["user_id"]),
        }
    }


def top_expenses() -> dict:
    """Returns a dictionary with the following structure:
    top_expenses: [
        {
            category (string)
            amount (float)
        },
        ...
    ]
    """

    transactions = crud_transaction.get_transactions_by_month(
        session["user_id"], get_active_date()
    )
    categories = {}
    category_ids = {}
    for txn in transactions:
        if txn.amount > 0 or txn.category_id is None:
            continue

        if txn.category_id not in category_ids:
            category_ids[txn.category_id] = crud_category.get_category_by_id(
                txn.category_id
            )

        category = category_ids[txn.category_id].name
        if category not in categories:
            categories[category] = 0.0

        categories[category] += abs(txn.amount)

    return {
        "top_expenses": sorted(
            [{"category": c, "amount": amt} for c, amt in categories.items()],
            key=lambda x: x["amount"],
            reverse=True,
        )
    }


def recent_transactions() -> dict:
    return {
        "recent_transactions": [
            txn.model_dump()
            for txn in crud_transaction.get_transactions_by_month(
                session["user_id"], get_active_date()
            )
        ][-1:-6:-1],
        "total_transactions": crud_transaction.count_transactions_by_month(
            session["user_id"], get_active_date()
        ),
    }


def budget_status() -> dict:
    """Returns a dictionary with the following structure:
    budget_status: [
        {
            category (string)
            percentage (int)
            status_color (string): 'success', 'warning', or 'danger'
        }
        ...
    ]
    """
    budgets = crud_budget.get_budgets_by_user_id(session["user_id"])
    transactions = crud_transaction.get_transactions_by_month(
        session["user_id"], get_active_date()
    )
    category_buckets = {}
    for txn in transactions:
        if txn.category_id not in category_buckets:
            category_buckets[txn.category_id] = 0.0
        category_buckets[txn.category_id] += -(txn.amount)

    categories = {
        c.id: c.name for c in crud_category.get_categories_by_user(session["user_id"])
    }

    # https://docs.python.org/3/library/heapq.html
    # "Heap elements can be tuples. This is useful for assigning comparison
    # values (such as task priorities) alongside the main record being tracked"
    # Note: heapq implements a min-heap so negate the percentage to replicate max-heap
    budget_status_ = []
    for b in budgets:
        category = categories.get(b.category_id, "Unknown")
        neg_percentage = -int(
            math.ceil(category_buckets.get(b.category_id, 0) / b.amount * 100)
        )
        heapq.heappush(budget_status_, (neg_percentage, category))

    display_list = []
    num_overbudget = 0
    while budget_status_ and len(display_list) < 5:
        neg_percentage, category = heapq.heappop(budget_status_)

        if -neg_percentage == 100:
            # Skip categories that are exactly 100% spent
            continue
        elif -neg_percentage > 100:
            num_overbudget += 1

        display_list.append(
            {
                "category": category,
                "percentage": -neg_percentage,
                "status_color": ui.budget_color(-neg_percentage),
            }
        )

    return {"budget_status": display_list, "num_overbudget": num_overbudget}


def chart() -> dict:
    chart_type = get_active_chart()

    transactions = crud_transaction.get_transactions_by_month(
        session["user_id"], get_active_date()
    )

    if chart_type == "category":
        chart_html = charts.category_pie_chart(transactions)
    elif chart_type == "dailySpending":
        chart_html = charts.daily_spending_chart(transactions)
    else:
        chart_html = "Contents..."

    return {"active_chart": chart_type, "chart_html": chart_html}


def saving_goals() -> dict:
    """Returns a dictionary with the following structure:
    {
        goals: [
            {
                name (string)
                target_amount (float)
                current_amount (float)
            },
            ...
        ]
    }
    """
    return {
        "goals": [
            goal.model_dump()
            for goal in crud_goal.get_goals_by_user(session["user_id"])
        ]
    }


def available_history() -> dict:
    """Returns a dictionary with the following structure:
    {
        available_history: [
                {
                    value: (string),
                    label: (float)
                }
            ...
        ],
        active_month_value: (string) Y-m
    }
    """
    available_months = [
        {
            "value": f"{int(year):04d}-{int(month):02d}",
            "label": datetime.datetime(int(year), int(month), 1).strftime("%B %Y"),
        }
        for year, month in crud_transaction.get_available_months(session["user_id"])
    ]

    return {
        "available_months": available_months,
        "active_month_value": (get_active_date().strftime("%Y-%m")),
    }


def user_notifications() -> dict:
    """Returns a dictionary with the following structure:
    {
        notifications: [
            {
                type (string)
                message (string)
            },
            ...
        ]
    }
    """
    return {"notifications": []}
