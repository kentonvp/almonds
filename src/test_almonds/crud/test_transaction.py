from datetime import datetime, timedelta
from uuid import UUID, uuid4

import pydantic
import pytest

from almonds.crud.transaction import (
    create_transaction,
    get_transaction_by_id,
    get_transactions_by_user,
    update_transaction,
)
from almonds.models.transaction import Transaction as TransactionModel
from almonds.schemas.transaction import Transaction, TransactionBase


@pytest.fixture
def sample_transaction_base():
    return TransactionBase(
        user_id=uuid4(),
        category_id=1,
        amount=100.00,
        description="Transaction Description",
        datetime=datetime.utcnow(),
    )


def test_create_transaction(sessionmaker_test, sample_transaction_base):
    created_transaction = create_transaction(
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
    created_transaction = create_transaction(
        sample_transaction_base, sessionmaker=sessionmaker_test
    )

    retrieved_transaction = get_transaction_by_id(
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
    created_transaction1 = create_transaction(
        sample_transaction_base, sessionmaker=sessionmaker_test
    )
    created_transaction2 = create_transaction(
        sample_transaction_base, sessionmaker=sessionmaker_test
    )

    retrieved_transactions = get_transactions_by_user(
        sample_transaction_base.user_id, sessionmaker=sessionmaker_test
    )

    assert len(retrieved_transactions) == 2
    assert set(tx.id for tx in retrieved_transactions) == {
        created_transaction1.id,
        created_transaction2.id,
    }


def test_update_transaction(sessionmaker_test, sample_transaction_base):
    created_transaction = create_transaction(
        sample_transaction_base, sessionmaker=sessionmaker_test
    )

    updated_transaction = Transaction(
        **(
            created_transaction.model_dump()
            | {"amount": 200.00, "description": "Updated Transaction"}
        )
    )

    result = update_transaction(updated_transaction, sessionmaker=sessionmaker_test)

    assert result.amount == 200.00
    assert result.description == "Updated Transaction"

    # Verify the update in the database
    retrieved_transaction = get_transaction_by_id(
        created_transaction.id, sessionmaker=sessionmaker_test
    )
    assert isinstance(retrieved_transaction, Transaction)
    assert retrieved_transaction.amount == 200.00
    assert retrieved_transaction.description == "Updated Transaction"


def test_get_nonexistent_transaction(sessionmaker_test):
    non_existent_id = uuid4()
    retrieved_transaction = get_transaction_by_id(
        non_existent_id, sessionmaker=sessionmaker_test
    )
    assert retrieved_transaction is None


def test_get_transactions_by_user_no_transactions(sessionmaker_test):
    user_id = uuid4()
    retrieved_transactions = get_transactions_by_user(
        user_id, sessionmaker=sessionmaker_test
    )
    assert retrieved_transactions == []


def test_update_nonexistent_transaction(sessionmaker_test, sample_transaction_base):
    non_existent_transaction = Transaction(
        id=uuid4(), **sample_transaction_base.model_dump()
    )

    # This should not raise an exception, but should return the transaction unchanged
    with pytest.raises(pydantic.ValidationError):
        update_transaction(non_existent_transaction, sessionmaker=sessionmaker_test)
