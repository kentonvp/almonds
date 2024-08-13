import datetime

from flask import Blueprint, redirect, request, session, url_for

from almonds.crud import transaction as crud_transaction
from almonds.schemas.transaction import TransactionBase

transaction_bp = Blueprint("transaction", __name__)


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
    return redirect(url_for("root.transactions", page=1))
