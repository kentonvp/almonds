import datetime
from concurrent.futures.thread import ThreadPoolExecutor
from uuid import UUID

from almonds.crud.plaid.plaid_item import get_items_for_user, update_cursor
from almonds.crud.transaction import create_transactions
from almonds.crud.user import most_recently_logged_in
from almonds.crypto.cryptograph import Cryptograph
from almonds.schemas.transaction import TransactionBase
from almonds.schemas.user import User
from almonds.services.plaid import core as plaid_core


def parse_transaction(
    transaction: dict, *, user_id: UUID, item_id: UUID
) -> TransactionBase:
    merchant_name = transaction["merchant_name"] or transaction["name"]
    amount = transaction["amount"] * -1.0

    if transaction["authorized_datetime"]:
        dt = transaction["authorized_datetime"]
    elif transaction["authorized_date"]:
        dt = datetime.datetime.fromisoformat(transaction["authorized_date"].isoformat())
    else:
        dt = datetime.datetime.fromisoformat(transaction["date"].isoformat())

    pending = transaction["pending"]

    return TransactionBase(
        user_id=user_id,
        category_id=None,
        amount=amount,
        description=merchant_name,
        datetime=dt,
        pending=pending,
        item_id=item_id,
    )


def update_user_transactions(user: User, *, cryptograph: Cryptograph = None):
    items = get_items_for_user(user.id)
    for it in items:
        access_token = cryptograph.decrypt(it.access_token)

        result = plaid_core.sync_transactions(access_token, cursor=it.cursor)

        added: list[TransactionBase] = []
        for txn in result.added:
            t = parse_transaction(txn, user_id=user.id, item_id=it.id)
            added.append(t)

        # add new transactions to database
        create_transactions(added)

        # todo: modified
        for tx in result.modified:
            t = parse_transaction(tx, user_id=user.id, item_id=it.id)
            # update_transactions(t)

        # todo: removed

        # save the cursor
        update_cursor(it.id, result.cursor)

        # todo: update balances
        # for acc in result.accounts:
        #     update_account_balance(acc.id, acc.balance)


def sync_transactions(*, cryptograph: Cryptograph = None):
    users = most_recently_logged_in(limit=10)

    with ThreadPoolExecutor() as executor:
        for user in users:
            executor.submit(update_user_transactions, user, cryptograph=cryptograph)
