import os

from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products

from almonds.services.plaid.client import client


def create_link_token() -> str:
    resp = client.link_token_create(
        LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id="test_user1"),
            client_name="Almonds",
            language="en",
            products=[Products("auth")],
            country_codes=[CountryCode("US")],
            redirect_uri=os.getenv("PLAID_SANDBOX_REDIRECT_URI"),
        )
    )

    return resp["link_token"]


def exchange_public_token(public_token: str) -> dict:
    req = ItemPublicTokenExchangeRequest(public_token=public_token)
    resp = client.item_public_token_exchange(req)
    return resp
