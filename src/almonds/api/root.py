import datetime

# tmp
import random

import pandas as pd
import plotly.graph_objects as go
from flask import Blueprint, redirect, render_template, session, url_for

import almonds.crud.category as crud_category
import almonds.crud.transaction as crud_transaction

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
    context |= top_expsenses()
    context |= recent_transactions()
    context |= budget_status()
    context |= spending_chart()

    return render_template("root.html", **context)


@root.route("/budget")
def budget():
    if "username" not in session:
        return redirect(url_for("root.view"))

    context = build_context()
    return render_template(
        "budget.html",
        current_page="budget",
        user={"username": session["username"]},
        **context
    )


@root.route("/goals")
def goals():
    if "username" not in session:
        return redirect(url_for("root.view"))

    context = build_context()
    return render_template(
        "goals.html",
        current_page="goals",
        user={"username": session["username"]},
        **context
    )


@root.route("/settings")
def settings():
    if "username" not in session:
        return redirect(url_for("root.view"))

    context = build_context()
    return render_template(
        "settings.html",
        current_page="settings",
        user={"username": session["username"]},
        **context
    )


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

    transactions = crud_transaction.get_transactions_by_month(session["user_id"])
    categories = {}
    category_ids = {}
    for txn in transactions:
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
