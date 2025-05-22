import datetime
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

from almonds.api import home
from almonds.crud import category as crud_category
from almonds.crud import transaction as crud_transaction
from almonds.schemas.transaction import Transaction, TransactionBase
from almonds.utils import status_code

transaction_bp = Blueprint("transactions", __name__)

TRANSACTION_LIMIT = 25


@transaction_bp.route("/", defaults={"page": 1}, methods=["GET"])
@transaction_bp.route("/<int:page>", methods=["GET"])
def view(page: int):
    if "username" not in session:
        return redirect(url_for("root.view"))

    set_page_number(page)

    page_transactions = crud_transaction.get_transactions_by_user(
        session["user_id"],
        limit=TRANSACTION_LIMIT,
        offset=(page - 1) * TRANSACTION_LIMIT,
    )

    user_categories = crud_category.get_categories_by_user(session["user_id"])
    categories_map = {}
    for c in user_categories:
        categories_map[c.id] = c.name

    display_transactions = [
        txn.model_dump()
        | {"category": categories_map.get(txn.category_id, "Uncategorized")}
        for txn in page_transactions
    ]

    context = build_context()
    context |= {
        "categories": user_categories,
        "transactions": display_transactions,
    }
    return render_template("transactions.html", **context)


@transaction_bp.route("/get", methods=["POST"])
def get_transaction():
    # get transaction_id from body of request
    body = request.get_json()
    if "transaction_id" not in body:
        return (
            jsonify({"error": "Transaction ID not provided"}),
            status_code.HTTP_400_BAD_REQUEST,
        )

    transaction_id = UUID(body["transaction_id"])
    txn = crud_transaction.get_transaction_by_id(transaction_id)
    if txn:
        datestr = txn.datetime.strftime("%Y-%m-%d")
        return jsonify(txn.model_dump() | {"date": datestr}), status_code.HTTP_200_OK

    return jsonify({"error": "Transaction not found"}), status_code.HTTP_404_NOT_FOUND


@transaction_bp.route("/create", methods=["POST"])
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
        pending=False,
        item_id=None,
    )

    crud_transaction.create_transaction(transaction)
    return redirect(url_for("transactions.view", page=get_page_number()))


@transaction_bp.route("/update", methods=["POST"])
def update_transaction():
    tid = UUID(request.form["transaction-id"])
    txn = crud_transaction.get_transaction_by_id(tid)

    is_expense = -1 if request.form["transaction-type"] == "expense" else 1

    transaction = Transaction(
        id=UUID(request.form["transaction-id"]),
        user_id=session["user_id"],
        amount=float(request.form["transaction-amount"]) * is_expense,
        category_id=int(request.form["transaction-category"]),
        description=request.form["transaction-description"],
        datetime=datetime.datetime.strptime(
            request.form["transaction-date"], "%Y-%m-%d"
        ),
        pending="transaction-pending" in request.form,
        item_id=txn.item_id,
    )

    crud_transaction.update_transaction(transaction)
    return redirect(url_for("transactions.view", page=get_page_number()))


@transaction_bp.route("/delete", methods=["POST"])
def delete_transaction():
    # get transaction_id from body of request
    body = request.get_json()
    if "transaction_id" not in body:
        return (
            jsonify({"error": "Transaction ID not provided"}),
            status_code.HTTP_400_BAD_REQUEST,
        )

    transaction_id = UUID(body["transaction_id"])
    crud_transaction.delete_transaction(transaction_id)
    return redirect(url_for("transactions.view", page=get_page_number()))


@transaction_bp.route("/filter", methods=["POST"])
def filter_form():
    recent_days = int(request.form["date-range"])
    category = request.form["category"]
    type_ = request.form["type"]
    search = request.form["search"]

    categories_map = {}
    user_categories = crud_category.get_categories_by_user(session["user_id"])
    for c in user_categories:
        categories_map[c.id] = c.name

    # TODO: Do the filtering in SQL
    transactions = crud_transaction.get_transactions_by_user(session["user_id"])
    display_transactions = [
        txn.model_dump()
        | {"category": categories_map.get(txn.category_id, "Uncategorized")}
        for txn in transactions
        if (
            txn.datetime
            > datetime.datetime.now() - datetime.timedelta(days=recent_days)
            and (category == "" or category == txn.category_id)
            and (
                type_ == ""
                or (type_ == "expense" and txn.amount < 0)
                or (type_ == "income" and txn.amount > 0)
            )
            and (search == "" or search in txn.description)
        )
    ]

    context = build_context()
    context |= {
        "categories": user_categories,
        "transactions": display_transactions,
    }
    return render_template("transactions.html", **context)


@transaction_bp.route("/resetFilter", methods=["POST"])
def reset_filter():
    return redirect(url_for("transactions.view", page=get_page_number()))


def get_page_number() -> int:
    return session.get("page_num", 1)


def set_page_number(page: int) -> None:
    session["page_num"] = page


def get_pagination_page() -> dict:
    """
    Get the page number from the session or default to 1.
    """
    page = get_page_number()

    total_pages = (
        crud_transaction.count_transactions(session["user_id"]) // TRANSACTION_LIMIT + 1
    )

    start_page = max(1, page - 2)
    end_page = min(total_pages, start_page + 4)

    if end_page - start_page < 4:
        start_page = max(1, end_page - 4)

    return {
        "pagination": {
            "curr": page,
            "total": total_pages,
            "start": start_page,
            "end": end_page,
        }
    }


def build_context(**kwargs) -> dict:
    context = home.build_context()
    context |= {
        "title": "Transactions",
        "user": {"username": session["username"]},
        "current_page": "transactions",
    }
    context |= get_pagination_page()
    return context | kwargs
