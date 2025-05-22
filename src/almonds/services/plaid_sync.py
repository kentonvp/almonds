import datetime
from concurrent.futures.thread import ThreadPoolExecutor
from uuid import UUID

import almonds.crud.plaid.account as plaid_account
import almonds.crud.plaid.transaction as plaid_transaction
import almonds.crud.transaction as crud_transaction
from almonds.crud.plaid import plaid_item
from almonds.crud.user import most_recently_logged_in
from almonds.crypto.cryptograph import Cryptograph
from almonds.schemas.plaid.account import PlaidAccountBase
from almonds.schemas.plaid.transaction import PlaidTransactionBase
from almonds.schemas.transaction import TransactionBase
from almonds.schemas.user import User
from almonds.services.plaid import core as plaid_core
from almonds.services.plaid_transaction_category_map import PLAID_TO_ALMONDS_CATEGORY


def parse_transaction(
    transaction: dict, *, user_id: UUID, item_id: UUID
) -> TransactionBase:
    # https://plaid.com/docs/api/products/transactions/#transactions-sync-response-added
    merchant_name = transaction["merchant_name"] or transaction["name"]
    amount = transaction["amount"] * -1.0

    if transaction["authorized_datetime"]:
        dt = transaction["authorized_datetime"]
    elif transaction["authorized_date"]:
        dt = datetime.datetime.fromisoformat(transaction["authorized_date"].isoformat())
    else:
        dt = datetime.datetime.fromisoformat(transaction["date"].isoformat())

    pending = transaction["pending"]

    category_id = None
    pf_cat = transaction.get("personal_finance_category")
    if pf_cat and "HIGH" in pf_cat["confidence_level"]:
        detailed = pf_cat["detailed"]
        category_id = PLAID_TO_ALMONDS_CATEGORY.get(detailed)

    return TransactionBase(
        user_id=user_id,
        category_id=category_id,
        amount=amount,
        description=merchant_name,
        datetime=dt,
        pending=pending,
        item_id=item_id,
    )


def parse_account(account: dict, *, user_id: UUID) -> PlaidAccountBase:
    # https://plaid.com/docs/api/products/transactions/#transactions-sync-response-accounts
    return PlaidAccountBase(
        user_id=user_id,
        account_id=account["account_id"],
        balance=account["balances"]["current"],
        cursor=None,
    )


def added_transactions_handler(transactions: list, *, user_id: UUID, item_id: UUID):
    """
    Add new transactions to the database. If a transaction already exists, skip it.
    """

    added: list[TransactionBase] = []
    for txn in transactions:
        # check if transaction has been pulled already
        if plaid_transaction.get_transaction_by_plaid_id(txn["transaction_id"]):
            continue

        t = parse_transaction(txn, user_id=user_id, item_id=item_id)

        # add plaid_transaction (todo: batch like crud_transaction?)
        plaid_transaction.create_transaction(
            PlaidTransactionBase(
                account_id=txn["account_id"],
                transaction_id=txn["transaction_id"],
            )
        )

        added.append(t)

    crud_transaction.create_transactions(added)


def update_accounts_handler(accounts: list, *, user_id: UUID):
    """
    Update accounts in the database. If an account does not exist, create it.
    """

    for raw_account in accounts:
        base = parse_account(raw_account, user_id=user_id)
        account = plaid_account.get_account_by_plaid_id(base.account_id)
        if account is None:
            plaid_account.create_account(base)
        else:
            # Update existing account
            account.balance = base.balance
            plaid_account.update_account(account)


def sync_user(user: User, *, cryptograph: Cryptograph):
    """Sync plaid transactions for a user."""

    items = plaid_item.get_active_items_for_user(user.id)

    for it in items:
        access_token = cryptograph.decrypt(it.access_token)

        result = plaid_core.sync_transactions(user.id, access_token, cursor=it.cursor)

        # update accounts
        update_accounts_handler(result.accounts, user_id=user.id)

        # add new transactions to database
        added_transactions_handler(result.added, user_id=user.id, item_id=it.id)

        # todo: modified
        # https://plaid.com/docs/api/products/transactions/#transactions-sync-response-modified

        # todo: removed
        # https://plaid.com/docs/api/products/transactions/#transactions-sync-response-removed

        # save the cursor
        plaid_item.update_cursor(it.id, result.cursor)


def sync(cryptograph: Cryptograph):
    users = most_recently_logged_in(limit=10)

    with ThreadPoolExecutor() as executor:
        for user in users:
            executor.submit(sync_user, user, cryptograph=cryptograph)
