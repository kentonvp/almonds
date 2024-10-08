import heapq
import math

from flask import Blueprint, redirect, render_template, session, url_for

import almonds.crud.budget as crud_budget
import almonds.crud.category as crud_category
import almonds.crud.goal as crud_goal
import almonds.crud.transaction as crud_transaction
from almonds.utils import ui

root = Blueprint("root", __name__)


@root.route("/")
def view():
    if "username" not in session:
        context = build_context()
        return render_template("login.html", **context)

    context = build_context(
        current_page="root",
        plaid_access_token=session.get("access_token"),
        plaid_item_id=session.get("item_id"),
    )

    context |= user_context()
    context |= top_expenses()
    context |= recent_transactions()
    context |= budget_status()
    context |= spending_chart()
    context |= saving_goals()

    return render_template("root.html", **context)


@root.route("/settings")
def settings():
    if "username" not in session:
        return redirect(url_for("root.view"))

    context = build_context()
    return render_template("settings.html", current_page="settings", **context)


@root.route("/plaidLogin")
def plaid_login():
    return render_template("plaid.html")


@root.route("/oauth")
def oauth_login():
    return render_template("oauth.html")


# Helper functions ////////////////////////////////////////////////////////////
def build_context(**kwargs) -> dict:
    base = {
        "title": "Dashboard",
    }

    if "user_id" in session:
        base["user"] = {"username": session["username"]}

    return base | kwargs


def user_context() -> dict:
    """Returns a dictionary with the following structure:
    user: {
        username (string)
        total_balance (float)
        income_this_month (float)
        expenses_this_month (float)
        savings_goal_progress: [
            {
                name (string)
                progress (int)
            },
            ...
        ]
    }
    """
    transactions = crud_transaction.get_transactions_by_month(session["user_id"])

    income = 0.0
    expense = 0.0

    for txn in transactions:
        if txn.amount > 0:
            income += txn.amount
        else:
            expense += txn.amount

    return {
        "user": {
            "username": session["username"],
            "total_balance": income + expense,
            "income_this_month": income,
            "expenses_this_month": abs(expense),
            "savings_goal_progress": 0.0,
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

    transactions = crud_transaction.get_transactions_by_month(session["user_id"])
    categories = {}
    category_ids = {}
    for txn in transactions:
        if txn.amount > 0:
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
            for txn in crud_transaction.get_transactions_by_user(
                session["user_id"], limit=5
            )
        ],
        "total_transactions": crud_transaction.count_transactions_by_month(
            session["user_id"]
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
    transactions = crud_transaction.get_transactions_by_month(session["user_id"])
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


def spending_chart() -> dict:
    """Returns a dictionary with the following structure:
    {
        spending_chart (string html)
    }
    """
    return {"spending_chart": "<pre>Contents</pre>"}


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
