from flask import Blueprint, redirect, render_template, request, session, url_for

root = Blueprint("root", __name__)


def build_context(**kwargs) -> dict:
    base = {
        "title": "Dashboard",
    }

    if "username" in session:
        base["username"] = session["username"]

    return base | kwargs


@root.route("/")
def view():
    if "username" not in session:
        context = build_context()
        return render_template("login.html", **context)

    context = build_context(current_page="root")

    """"
    user: {
        username (string)
        total_balance (float)
        income_this_month (float)
        expenses_this_month (float)
        savings_goal_progress (int)
    }
    """
    context |= {
        "user": {
            "total_balance": 0.0,
            "income_this_month": 0.0,
            "expenses_this_month": 0.0,
            "savings_goal_progress": 0,
        }
    }

    """
    top_expenses: [
        {
            category (string)
            amount (float)
        }
        ...
    ]
    """
    context |= {"top_expenses": []}

    """
    recent_transactions: [
        {
            description (string)
            date (datetime)
            amount (float)
        }
        ...
    ]
    """
    context |= {"recent_transactions": []}

    """
    budget_status: [
        {
            category (string)
            percentage (int)
            status_color (string): 'success', 'warning', or 'danger'
        }
        ...
    ]
    """
    context |= {"budget_status": []}

    """
    spending_chart (string html)
    """
    context |= {"spending_chart": "<div>Chart Goes Here</div>"}
    return render_template("root.html", **context)


@root.route("/transactions/<int:page>")
def transactions(page: int):
    if "username" not in session:
        return redirect(url_for("root.view"))

    context = build_context()
    context |= {
        "categories": [
            # {id, name}
        ],
        "transactions": [
            # {id, date, description, category, amount}
        ],
        "pagination": {"page_n": page, "total_pages": 1},
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
