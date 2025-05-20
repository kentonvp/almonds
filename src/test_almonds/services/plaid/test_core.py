from uuid import UUID

import pytest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.item_get_request import ItemGetRequest
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest

from almonds.services.plaid.core import (
    create_link_token,
    exchange_public_token,
    get_balance,
    get_item_info,
    sync_transactions,
)


@pytest.fixture
def mock_plaid_client(monkeypatch):
    class MockClient:
        def link_token_create(self, _: LinkTokenCreateRequest):
            print("HERE in Mock!")
            return {"link_token": "link-sandbox-12345"}

        def item_public_token_exchange(self, _: ItemPublicTokenExchangeRequest):
            return {
                "access_token": "access-sandbox-12345",
                "item_id": "item-sandbox-12345",
            }

        def accounts_balance_get(self, _: AccountsBalanceGetRequest):
            return {
                "accounts": [
                    {
                        "account_id": "account-sandbox-12345",
                        "balances": {
                            "available": 100.00,
                            "current": 110.00,
                            "limit": None,
                        },
                    }
                ]
            }

        def transactions_sync(self, request: TransactionsSyncRequest):
            # Simulate pagination based on cursor
            if not hasattr(request, "cursor") or request.cursor == None:
                return {
                    "added": [{"transaction_id": "1"}, {"transaction_id": "2"}],
                    "modified": [{"transaction_id": "3"}],
                    "removed": [],
                    "has_more": True,
                    "next_cursor": "cursor-12345",
                    "accounts": [{"account_id": "1"}, {"account_id": "2"}],
                }
            else:
                return {
                    "added": [],
                    "modified": [],
                    "removed": [{"transaction_id": "2"}],
                    "has_more": False,
                    "next_cursor": "cursor-67890",
                    "accounts": [{"account_id": "1"}, {"account_id": "2"}],
                }

        def item_get(self, _: ItemGetRequest):
            return {
                "item": {
                    "item_id": "item-sandbox-12345",
                    "institution_id": "ins_12345",
                    "institution_name": "First Platypus Bank",
                    "status": {
                        "transactions": {
                            "last_successful_update": "2023-01-01T12:00:00Z"
                        }
                    },
                }
            }

    monkeypatch.setattr("almonds.services.plaid.core.client", MockClient())


@pytest.fixture
def sample_user_id():
    return UUID("12345678-1234-5678-1234-567812345678")


def test_create_link_token(mock_plaid_client, sample_user_id, monkeypatch):
    monkeypatch.setenv("PLAID_SANDBOX_REDIRECT_URI", "https://127.0.0.1:5000/oath")

    # Act
    result = create_link_token(sample_user_id)

    # Assert
    assert result == "link-sandbox-12345"


def test_exchange_public_token(mock_plaid_client):
    # Arrange
    public_token = "public-sandbox-12345"

    # Act
    result = exchange_public_token(public_token)

    # Assert
    assert result["access_token"] == "access-sandbox-12345"
    assert result["item_id"] == "item-sandbox-12345"


def test_get_balance(mock_plaid_client):
    # Arrange
    access_token = "access-sandbox-12345"

    # Act
    result = get_balance(access_token)

    # Assert
    assert "accounts" in result
    assert len(result["accounts"]) == 1
    assert result["accounts"][0]["balances"]["available"] == 100.00
    assert result["accounts"][0]["balances"]["current"] == 110.00


def test_sync_transactions(mock_plaid_client, monkeypatch):
    monkeypatch.setenv("ALMONDS_ENVIRONMENT", "sandbox")

    # Arrange
    access_token = "access-sandbox-12345"

    # Act
    result = sync_transactions(access_token)
    print(result)

    # Assert
    assert len(result.added) == 2
    assert len(result.modified) == 1
    assert len(result.removed) == 1


def test_get_item_info(mock_plaid_client):
    # Arrange
    access_token = "access-sandbox-12345"

    # Act
    result = get_item_info(access_token)

    # Assert
    assert result["item_id"] == "item-sandbox-12345"
    assert result["institution_id"] == "ins_12345"
    assert result["institution_name"] == "First Platypus Bank"
    assert "status" in result
    assert "transactions" in result["status"]
