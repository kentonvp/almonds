from uuid import uuid4

from almonds.crud.plaid.transaction import (
    create_transaction,
    delete_transaction,
    get_transaction,
    get_transaction_by_plaid_id,
)
from almonds.schemas.plaid.transaction import PlaidTransactionBase


def test_create_and_get_transaction(sessionmaker_test):
    account_id = "account_abc"
    plaid_transaction_id = "plaid_txn_123"

    txn_base = PlaidTransactionBase(
        account_id=account_id,
        transaction_id=plaid_transaction_id,
    )

    # Create
    created = create_transaction(txn_base, sessionmaker=sessionmaker_test)
    assert created.account_id == account_id
    assert created.transaction_id == plaid_transaction_id
    assert created.id is not None

    # Get by id
    fetched = get_transaction(created.id, sessionmaker=sessionmaker_test)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.account_id == account_id
    assert fetched.transaction_id == plaid_transaction_id

    # Get by plaid_id
    fetched_by_plaid = get_transaction_by_plaid_id(
        plaid_transaction_id, sessionmaker=sessionmaker_test
    )
    assert fetched_by_plaid is not None
    assert fetched_by_plaid.id == created.id


def test_get_transaction_not_found(sessionmaker_test):
    random_id = uuid4()
    assert get_transaction(random_id, sessionmaker=sessionmaker_test) is None
    assert (
        get_transaction_by_plaid_id("nonexistent", sessionmaker=sessionmaker_test)
        is None
    )


def test_delete_transaction(sessionmaker_test):
    account_id = "account_del"
    plaid_transaction_id = "plaid_txn_del"

    txn_base = PlaidTransactionBase(
        account_id=account_id,
        transaction_id=plaid_transaction_id,
    )

    created = create_transaction(txn_base, sessionmaker=sessionmaker_test)
    # Confirm exists
    assert get_transaction(created.id, sessionmaker=sessionmaker_test) is not None

    # Delete
    delete_transaction(created.id, sessionmaker=sessionmaker_test)

    # Confirm deleted
    assert get_transaction(created.id, sessionmaker=sessionmaker_test) is None
    assert (
        get_transaction_by_plaid_id(
            plaid_transaction_id, sessionmaker=sessionmaker_test
        )
        is None
    )
