import os
from uuid import UUID

from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.country_code import CountryCode
from plaid.model.item_get_request import ItemGetRequest
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.transactions_sync_request import TransactionsSyncRequest

from almonds import config
from almonds.services.plaid.client import client


def create_link_token(user_id: UUID) -> str:
    resp = client.link_token_create(
        LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id=str(user_id)),
            client_name="Almonds",
            language="en",
            products=[Products("transactions")],
            country_codes=[CountryCode("US")],
            redirect_uri=os.getenv("PLAID_SANDBOX_REDIRECT_URI"),
        )
    )

    return resp["link_token"]


def exchange_public_token(public_token: str) -> dict:
    req = ItemPublicTokenExchangeRequest(public_token=public_token)
    resp = client.item_public_token_exchange(req)
    return resp


def get_balance(access_token: str) -> dict:
    req = AccountsBalanceGetRequest(access_token=access_token)
    resp = client.accounts_balance_get(req)
    return resp


def sync_transactions(access_token: str, *, cursor: str | None = None) -> dict:
    transactions = {}
    transactions["added"] = []
    transactions["modified"] = []
    transactions["removed"] = []
    transactions["cursor"] = cursor
    has_more = True

    # the transactions in the responses are paginated, so make multiple calls
    # while incrementing the cursor to retrieve all transactions
    while has_more:
        req = TransactionsSyncRequest(
            access_token=access_token,
            cursor=transactions["cursor"],
            _check_type=config.ALMONDS_ENV,
        )
        resp = client.transactions_sync(req)

        transactions["added"].extend(resp["added"])
        transactions["modified"].extend(resp["modified"])
        transactions["removed"].extend(resp["removed"])
        transactions["cursor"] = resp["next_cursor"]

        has_more = resp["has_more"]

    return transactions


def get_item_info(access_token: str) -> dict:
    req = ItemGetRequest(access_token=access_token)
    resp = client.item_get(req)
    return resp["item"]
