import os
from dataclasses import dataclass, field
from uuid import UUID

from plaid.model.country_code import CountryCode
from plaid.model.item_access_token_invalidate_request import (
    ItemAccessTokenInvalidateRequest,
)
from plaid.model.item_get_request import ItemGetRequest
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.item_remove_request import ItemRemoveRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.transactions_sync_request import TransactionsSyncRequest

import almonds.crud.plaid.request as crud_plaid_request
from almonds.schemas.plaid.request import RequestBase
from almonds.services.plaid.client import client


@dataclass
class TransactionResult:
    added: list = field(default_factory=list)
    modified: list = field(default_factory=list)
    removed: list = field(default_factory=list)
    cursor: str | None = field(default=None)
    accounts: list = field(default_factory=list)


def create_link_token(user_id: UUID) -> str:
    resp = client.link_token_create(
        LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id=str(user_id)),
            client_name="Almonds",
            language="en",
            products=[Products("transactions")],
            country_codes=[CountryCode("US")],
            redirect_uri=os.getenv("PLAID_REDIRECT_URI"),
        )
    )

    crud_plaid_request.create_request(
        RequestBase(
            request_id=resp["request_id"], user_id=user_id, call="create_link_token"
        )
    )

    return resp["link_token"]


def exchange_public_token(user_id: UUID, public_token: str) -> dict:
    req = ItemPublicTokenExchangeRequest(public_token=public_token)
    resp = client.item_public_token_exchange(req)

    crud_plaid_request.create_request(
        RequestBase(
            request_id=resp["request_id"], user_id=user_id, call="exchange_public_token"
        )
    )
    return resp


def rotate_access_token(user_id: UUID, access_token: str) -> str:
    req = ItemAccessTokenInvalidateRequest(access_token=access_token)
    resp = client.item_access_token_invalidate(req)

    crud_plaid_request.create_request(
        RequestBase(
            request_id=resp["request_id"], user_id=user_id, call="rotate_access_token"
        )
    )
    return resp["new_access_token"]


def sync_transactions(
    user_id: UUID, access_token: str, *, cursor: str | None = None
) -> TransactionResult:
    result = TransactionResult()

    # the transactions in the responses are paginated, so make multiple calls
    # while incrementing the cursor to retrieve all transactions
    has_more = True
    while has_more:
        req = TransactionsSyncRequest(
            access_token=access_token, cursor=result.cursor, _check_type=False
        )
        resp = client.transactions_sync(req)

        crud_plaid_request.create_request(
            RequestBase(
                request_id=resp["request_id"], user_id=user_id, call="transaction_sync"
            )
        )

        result.added.extend(resp["added"])
        result.modified.extend(resp["modified"])
        result.removed.extend(resp["removed"])

        result.cursor = resp["next_cursor"]
        result.accounts = resp["accounts"]

        has_more = resp["has_more"]

    return result


def get_item_info(user_id: UUID, access_token: str) -> dict:
    req = ItemGetRequest(access_token=access_token)
    resp = client.item_get(req)

    crud_plaid_request.create_request(
        RequestBase(
            request_id=resp["request_id"], user_id=user_id, call="get_item_info"
        )
    )
    return resp["item"]


def remove_item(user_id: UUID, access_token: str) -> bool:
    req = ItemRemoveRequest(access_token=access_token)
    resp = client.item_remove(req)

    crud_plaid_request.create_request(
        RequestBase(request_id=resp["request_id"], user_id=user_id, call="remove_item")
    )
    return True
