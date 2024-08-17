import datetime

from flask import Blueprint, redirect, render_template, request, session, url_for

from almonds.crud import category as crud_category
from almonds.crud import transaction as crud_transaction
from almonds.schemas.transaction import TransactionBase

transaction_bp = Blueprint("transactions", __name__)

TRANSACTION_LIMIT = 25


@transaction_bp.route("/", defaults={"page": 1})
@transaction_bp.route("/<int:page>")
def home(page: int):
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

    context = {"title": "Transactions", "user": {"username": session["username"]}}
    context |= {
        "categories": crud_category.get_categories_by_user(session["user_id"]),
        "transactions": display_transactions,
        "pagination": {"page_n": page, "total_pages": total_pages},
    }
    return render_template("transactions.html", current_page="transactions", **context)


@transaction_bp.route("/ceateTransaction", methods=["POST"])
def create_transaction():
    is_expense = -1 if request.form["transaction-type"] == "expense" else 1

    transaction = TransactionBase(
        user_id=session["user_id"],
        amount=float(request.form["transaction-amount"]) * is_expense,
        category_id=int(request.form["transaction-category"]),
        description=request.form["transaction-description"],
        datetime=datetime.datetime.strptime(
            request.form["transaction-date"], "%Y-%m-%d"
        ),
    )

    crud_transaction.create_transaction(transaction)
    return redirect(url_for("transactions.home"))


@transaction_bp.route("/transactionFilter", methods=["POST"])
def filter_form():
    return redirect(url_for("transactions.home"))
