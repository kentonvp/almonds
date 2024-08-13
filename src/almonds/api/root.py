import datetime

# tmp
import random

import pandas as pd
import plotly.graph_objects as go
from flask import Blueprint, redirect, render_template, session, url_for

import almonds.crud.category as crud_category
import almonds.crud.transaction as crud_transaction

root = Blueprint("root", __name__)

TRANSACTION_LIMIT = 25


def build_context(**kwargs) -> dict:
    base = {
        "title": "Dashboard",
    }

    if "username" in session:
        base["username"] = session["username"]

    return base | kwargs


def user_context() -> dict:
    """Returns a dictionary with the following structure:
    user: {
        username (string)
        total_balance (float)
        income_this_month (float)
        expenses_this_month (float)
        savings_goal_progress (int)
    }
    """
    return {
        "user": {
            "total_balance": 0.0,
            "income_this_month": 0.0,
            "expenses_this_month": 0.0,
            "savings_goal_progress": 0,
        }
    }


def top_expsenses() -> dict:
    """Returns a dictionary with the following structure:
    top_expenses: [
        {
            category (string)
            amount (float)
        }
        ...
    ]
    """
    return {
        "top_expenses": sorted(
            [
                {"category": "Food", "amount": 75.0},
                {"category": "Transportation", "amount": 75.0},
                {"category": "Travel", "amount": 800.0},
            ],
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
        ]
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
    return {
        "budget_status": sorted(
            [
                {"category": "Food", "percentage": 50, "status_color": "success"},
                {
                    "category": "Transportation",
                    "percentage": 25,
                    "status_color": "success",
                },
                {"category": "Travel", "percentage": 90, "status_color": "warning"},
            ],
            key=lambda x: x["percentage"],
            reverse=True,
        )
    }


def spending_chart() -> dict:
    """Returns a dictionary with the following structure:
    {
        spending_chart (string html)
    }
    """

    # Generate mock data
    end_date = datetime.datetime.now()
    dates_12m = pd.date_range(end=end_date, periods=12, freq="ME")
    spending_12m = [random.randint(500, 1500) for _ in range(12)]

    # Create DataFrame
    df = pd.DataFrame({"Date": dates_12m, "Spending": spending_12m})

    # Create traces for 3, 6, and 12 months
    trace_3m = go.Scatter(
        x=df["Date"][-3:], y=df["Spending"][-3:], mode="lines+markers", name="3 Months"
    )
    trace_6m = go.Scatter(
        x=df["Date"][-6:], y=df["Spending"][-6:], mode="lines+markers", name="6 Months"
    )
    trace_12m = go.Scatter(
        x=df["Date"], y=df["Spending"], mode="lines+markers", name="12 Months"
    )

    # Create layout
    layout = go.Layout(
        title="Monthly Spending Over Time",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Spending ($)"),
        legend=dict(x=0, y=1.1, orientation="h"),
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                active=2,
                x=0.57,
                y=1.2,
                buttons=list(
                    [
                        dict(
                            label="3 Months",
                            method="update",
                            args=[
                                {"visible": [True, False, False]},
                                {"title": "Monthly Spending - Last 3 Months"},
                            ],
                        ),
                        dict(
                            label="6 Months",
                            method="update",
                            args=[
                                {"visible": [False, True, False]},
                                {"title": "Monthly Spending - Last 6 Months"},
                            ],
                        ),
                        dict(
                            label="12 Months",
                            method="update",
                            args=[
                                {"visible": [False, False, True]},
                                {"title": "Monthly Spending - Last 12 Months"},
                            ],
                        ),
                    ]
                ),
            )
        ],
    )

    fig = go.Figure(data=[trace_3m, trace_6m, trace_12m], layout=layout)
    print(fig.to_html(full_html=False, include_plotlyjs="cdn"))

    return {"spending_chart": fig.to_html(full_html=False, include_plotlyjs="cdn")}


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
    context |= top_expsenses()
    context |= recent_transactions()
    context |= budget_status()
    context |= spending_chart()

    return render_template("root.html", **context)


@root.route("/transactions", defaults={"page": 1})
@root.route("/transactions/<int:page>")
def transactions(page: int):
    if "username" not in session:
        return redirect(url_for("root.view"))

    page_transactions = crud_transaction.get_transactions_by_user(
        session["user_id"],
        limit=TRANSACTION_LIMIT,
        offset=(page - 1) * TRANSACTION_LIMIT,
    )
    display_transactions = [
        txn.model_dump()
        | {
            "category": crud_category.get_category_by_id(
                session["user_id"], txn.category_id
            )
        }
        for txn in page_transactions
    ]

    total_pages = (
        crud_transaction.count_transactions(session["user_id"]) // TRANSACTION_LIMIT + 1
    )

    context = build_context()
    context |= {
        "categories": crud_category.get_categories_by_user(session["user_id"]),
        "transactions": display_transactions,
        "pagination": {"page_n": page, "total_pages": total_pages},
    }
    return render_template("transactions.html", current_page="transactions", **context)


@root.route("/budget")
def budget():
    if "username" not in session:
        return redirect(url_for("root.view"))

    context = build_context()
    return render_template("budget.html", current_page="budget", **context)


@root.route("/goals")
def goals():
    if "username" not in session:
        return redirect(url_for("root.view"))

    context = build_context()
    return render_template("goals.html", current_page="goals", **context)


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
