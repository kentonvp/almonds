import math
from uuid import uuid4

from almonds.crud.plaid.account import (
    create_account,
    delete_account,
    get_account,
    get_account_by_plaid_id,
    update_account,
)
from almonds.schemas.plaid.account import PlaidAccountBase


def test_create_and_get_account(sessionmaker_test):
    user_id = uuid4()
    plaid_account_id = "plaid_acc_123"
    balance = 12345.67
    cursor = "cursor_abc"

    account_base = PlaidAccountBase(
        user_id=user_id,
        account_id=plaid_account_id,
        balance=balance,
        cursor=cursor,
    )

    # Create
    created = create_account(account_base, sessionmaker=sessionmaker_test)
    assert created.user_id == user_id
    assert created.account_id == plaid_account_id
    assert created.cursor == cursor
    assert math.isclose(created.balance, balance, rel_tol=1e-9)
    assert created.id is not None

    # Get by id
    fetched = get_account(created.id, sessionmaker=sessionmaker_test)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.user_id == user_id
    assert fetched.account_id == plaid_account_id
    assert math.isclose(created.balance, balance, rel_tol=1e-9)
    assert fetched.cursor == cursor

    # Get by plaid_id
    fetched_by_plaid = get_account_by_plaid_id(
        plaid_account_id, sessionmaker=sessionmaker_test
    )
    assert fetched_by_plaid is not None
    assert fetched_by_plaid.id == created.id


def test_get_account_not_found(sessionmaker_test):
    random_id = uuid4()
    assert get_account(random_id, sessionmaker=sessionmaker_test) is None
    assert (
        get_account_by_plaid_id("nonexistent", sessionmaker=sessionmaker_test) is None
    )


def test_delete_account(sessionmaker_test):
    user_id = uuid4()
    plaid_account_id = "plaid_acc_del"
    balance = 12345.67
    cursor = None

    account_base = PlaidAccountBase(
        user_id=user_id,
        account_id=plaid_account_id,
        balance=balance,
        cursor=cursor,
    )

    created = create_account(account_base, sessionmaker=sessionmaker_test)
    # Confirm exists
    assert get_account(created.id, sessionmaker=sessionmaker_test) is not None

    # Delete
    delete_account(created.id, sessionmaker=sessionmaker_test)

    # Confirm deleted
    assert get_account(created.id, sessionmaker=sessionmaker_test) is None
    assert (
        get_account_by_plaid_id(plaid_account_id, sessionmaker=sessionmaker_test)
        is None
    )


def test_update_account(sessionmaker_test):
    user_id = uuid4()
    plaid_account_id = "plaid_acc_update"
    initial_balance = 12345.67
    updated_balance = 76543.21
    cursor = None

    account_base = PlaidAccountBase(
        user_id=user_id,
        account_id=plaid_account_id,
        balance=initial_balance,
        cursor=cursor,
    )

    created = create_account(account_base, sessionmaker=sessionmaker_test)

    # Update
    created.balance = updated_balance
    updated_account = update_account(created, sessionmaker=sessionmaker_test)

    # Confirm update
    fetched_updated = get_account(updated_account.id, sessionmaker=sessionmaker_test)
    assert fetched_updated is not None
    assert math.isclose(fetched_updated.balance, updated_balance, rel_tol=1e-9)
