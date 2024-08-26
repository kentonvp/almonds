import datetime
from uuid import UUID, uuid4

import pydantic
import pytest

import almonds.crud.transaction as crud_transaction
from almonds.schemas.transaction import Transaction, TransactionBase


@pytest.fixture
def sample_transaction_base():
    return TransactionBase(
        user_id=uuid4(),
        category_id=1,
        amount=100.00,
        description="Transaction Description",
        datetime=datetime.datetime.utcnow(),  # TODO: utcnow() is being deprecated
    )


def test_create_transaction(sessionmaker_test, sample_transaction_base):
    created_transaction = crud_transaction.create_transaction(
        sample_transaction_base, sessionmaker=sessionmaker_test
    )

    assert isinstance(created_transaction, Transaction)
    assert isinstance(created_transaction.id, UUID)
    assert created_transaction.amount == sample_transaction_base.amount
    assert created_transaction.description == sample_transaction_base.description
    assert created_transaction.datetime == sample_transaction_base.datetime
    assert created_transaction.user_id == sample_transaction_base.user_id
    assert created_transaction.category_id == sample_transaction_base.category_id


def test_get_transaction_by_id(sessionmaker_test, sample_transaction_base):
    created_transaction = crud_transaction.create_transaction(
        sample_transaction_base, sessionmaker=sessionmaker_test
    )

    retrieved_transaction = crud_transaction.get_transaction_by_id(
        created_transaction.id, sessionmaker=sessionmaker_test
    )

    assert retrieved_transaction is not None
    assert retrieved_transaction.id == created_transaction.id
    assert retrieved_transaction.amount == created_transaction.amount
    assert retrieved_transaction.description == created_transaction.description
    assert retrieved_transaction.datetime == created_transaction.datetime
    assert retrieved_transaction.user_id == created_transaction.user_id
    assert retrieved_transaction.category_id == created_transaction.category_id


def test_get_transactions_by_user(sessionmaker_test, sample_transaction_base):
    created_transaction1 = crud_transaction.create_transaction(
        sample_transaction_base, sessionmaker=sessionmaker_test
    )
    created_transaction2 = crud_transaction.create_transaction(
        sample_transaction_base, sessionmaker=sessionmaker_test
    )

    retrieved_transactions = crud_transaction.get_transactions_by_user(
        sample_transaction_base.user_id, sessionmaker=sessionmaker_test
    )

    assert len(retrieved_transactions) == 2
    assert set(tx.id for tx in retrieved_transactions) == {
        created_transaction1.id,
        created_transaction2.id,
    }


def test_get_transactions_by_user_with_limit(
    sessionmaker_test, sample_transaction_base
):
    created_transaction1 = crud_transaction.create_transaction(
        sample_transaction_base, sessionmaker=sessionmaker_test
    )
    # Add a second transaction but should not be retrieved.
    crud_transaction.create_transaction(
        sample_transaction_base, sessionmaker=sessionmaker_test
    )

    retrieved_transactions = crud_transaction.get_transactions_by_user(
        sample_transaction_base.user_id, limit=1, sessionmaker=sessionmaker_test
    )

    assert len(retrieved_transactions) == 1
    assert set(tx.id for tx in retrieved_transactions) == {
        created_transaction1.id,
    }


def test_get_transactions_by_user_with_offset(
    sessionmaker_test, sample_transaction_base
):
    # First should not be retrieved with offset.
    crud_transaction.create_transaction(
        sample_transaction_base, sessionmaker=sessionmaker_test
    )
    created_transaction2 = crud_transaction.create_transaction(
        sample_transaction_base, sessionmaker=sessionmaker_test
    )

    retrieved_transactions = crud_transaction.get_transactions_by_user(
        sample_transaction_base.user_id, offset=1, sessionmaker=sessionmaker_test
    )

    assert len(retrieved_transactions) == 1
    assert set(tx.id for tx in retrieved_transactions) == {
        created_transaction2.id,
    }


def test_update_transaction(sessionmaker_test, sample_transaction_base):
    created_transaction = crud_transaction.create_transaction(
        sample_transaction_base, sessionmaker=sessionmaker_test
    )

    updated_transaction = Transaction(
        **(
            created_transaction.model_dump()
            | {"amount": 200.00, "description": "Updated Transaction"}
        )
    )

    result = crud_transaction.update_transaction(
        updated_transaction, sessionmaker=sessionmaker_test
    )

    assert result.amount == 200.00
    assert result.description == "Updated Transaction"

    # Verify the update in the database
    retrieved_transaction = crud_transaction.get_transaction_by_id(
        created_transaction.id, sessionmaker=sessionmaker_test
    )
    assert isinstance(retrieved_transaction, Transaction)
    assert retrieved_transaction.amount == 200.00
    assert retrieved_transaction.description == "Updated Transaction"


def test_get_nonexistent_transaction(sessionmaker_test):
    non_existent_id = uuid4()
    retrieved_transaction = crud_transaction.get_transaction_by_id(
        non_existent_id, sessionmaker=sessionmaker_test
    )
    assert retrieved_transaction is None


def test_get_transactions_by_user_no_transactions(sessionmaker_test):
    user_id = uuid4()
    retrieved_transactions = crud_transaction.get_transactions_by_user(
        user_id, sessionmaker=sessionmaker_test
    )
    assert retrieved_transactions == []


def test_update_nonexistent_transaction(sessionmaker_test, sample_transaction_base):
    non_existent_transaction = Transaction(
        id=uuid4(), **sample_transaction_base.model_dump()
    )

    # This should not raise an exception, but should return the transaction unchanged
    with pytest.raises(pydantic.ValidationError):
        crud_transaction.update_transaction(
            non_existent_transaction, sessionmaker=sessionmaker_test
        )


def test_count_transactions(sessionmaker_test, sample_transaction_base):
    # Create 5 transactions
    for _ in range(5):
        crud_transaction.create_transaction(
            sample_transaction_base, sessionmaker=sessionmaker_test
        )

    user_id = sample_transaction_base.user_id
    count = crud_transaction.count_transactions(user_id, sessionmaker=sessionmaker_test)
    assert count == 5


def test_delete_transaction(sessionmaker_test, sample_transaction_base):
    created_transaction = crud_transaction.create_transaction(
        sample_transaction_base, sessionmaker=sessionmaker_test
    )

    crud_transaction.delete_transaction(
        created_transaction.id, sessionmaker=sessionmaker_test
    )

    retrieved_transaction = crud_transaction.get_transaction_by_id(
        created_transaction.id, sessionmaker=sessionmaker_test
    )
    assert retrieved_transaction is None


def test_delete_transaction_missing(sessionmaker_test):
    # Should not raise exception
    crud_transaction.delete_transaction(uuid4(), sessionmaker=sessionmaker_test)


def test_get_transactions_by_month(sessionmaker_test, sample_transaction_base):
    # Create 5 transactions
    for _ in range(5):
        crud_transaction.create_transaction(
            sample_transaction_base, sessionmaker=sessionmaker_test
        )

    user_id = sample_transaction_base.user_id
    today_ = sample_transaction_base.datetime.date()
    transactions = crud_transaction.get_transactions_by_month(
        user_id, today_, sessionmaker=sessionmaker_test
    )

    assert len(transactions) == 5

    user_id = sample_transaction_base.user_id
    today_ = sample_transaction_base.datetime.date() - datetime.timedelta(days=365)
    transactions = crud_transaction.get_transactions_by_month(
        user_id, today_, sessionmaker=sessionmaker_test
    )

    assert not transactions


def test_count_transactions_by_month(sessionmaker_test, sample_transaction_base):
    # Create 5 "old" transactions
    sample_transaction_base_OLD = TransactionBase(
        user_id=sample_transaction_base.user_id,
        category_id=sample_transaction_base.category_id,
        amount=sample_transaction_base.amount,
        description=sample_transaction_base.description,
        datetime=sample_transaction_base.datetime - datetime.timedelta(days=45),
    )

    for _ in range(5):
        crud_transaction.create_transaction(
            sample_transaction_base_OLD, sessionmaker=sessionmaker_test
        )

    # Create 10 current transactions
    for _ in range(10):
        crud_transaction.create_transaction(
            sample_transaction_base, sessionmaker=sessionmaker_test
        )

    user_id = sample_transaction_base.user_id
    today_ = sample_transaction_base.datetime.date()
    num_transactions = crud_transaction.count_transactions_by_month(
        user_id, today_, sessionmaker=sessionmaker_test
    )

    assert num_transactions == 10
