import datetime
from uuid import UUID, uuid4

import pytest
from sqlalchemy import create_engine

# Import the functions to be tested
from almonds.crud.budget import (
    create_budget,
    delete_budget,
    get_budget,
    get_budgets_by_user_id,
    update_budget,
)
from almonds.models.budget import Base
from almonds.models.budget import Budget as BudgetModel
from almonds.schemas.budget import Budget, BudgetBase


@pytest.fixture
def sample_budget_base():
    return BudgetBase(
        user_id=uuid4(),
        category_id=1,
        amount=1000.00,
        start_date=datetime.date(2024, 1, 24),
    )


def test_create_budget(sessionmaker_test, sample_budget_base):
    created_budget = create_budget(sample_budget_base, sessionmaker=sessionmaker_test)

    assert isinstance(created_budget, Budget)
    assert isinstance(created_budget.id, UUID)
    assert created_budget.amount == sample_budget_base.amount
    assert created_budget.user_id == sample_budget_base.user_id
    assert created_budget.category_id == sample_budget_base.category_id
    assert created_budget.start_date == sample_budget_base.start_date


def test_get_budget(sessionmaker_test, sample_budget_base):
    created_budget = create_budget(sample_budget_base, sessionmaker=sessionmaker_test)

    retrieved_budget = get_budget(created_budget.id, sessionmaker=sessionmaker_test)

    assert retrieved_budget is not None
    assert retrieved_budget.id == created_budget.id
    assert retrieved_budget.amount == created_budget.amount
    assert retrieved_budget.user_id == created_budget.user_id
    assert retrieved_budget.category_id == created_budget.category_id
    assert created_budget.start_date == sample_budget_base.start_date


def test_get_budgets_by_user_id(sessionmaker_test, sample_budget_base):
    created_budget1 = create_budget(sample_budget_base, sessionmaker=sessionmaker_test)
    created_budget2 = create_budget(sample_budget_base, sessionmaker=sessionmaker_test)

    retrieved_budgets = get_budgets_by_user_id(
        sample_budget_base.user_id, sessionmaker=sessionmaker_test
    )

    assert len(retrieved_budgets) == 2
    assert set(b.id for b in retrieved_budgets) == set(
        [created_budget1.id, created_budget2.id]
    )


def test_update_budget(sessionmaker_test, sample_budget_base):
    created_budget = create_budget(sample_budget_base, sessionmaker=sessionmaker_test)

    updated_budget = Budget(
        **(created_budget.model_dump() | {"category_id": 2, "amount": 1500.00})
    )

    result = update_budget(updated_budget, sessionmaker=sessionmaker_test)

    assert result.category_id == 2
    assert result.amount == 1500.00

    # Verify the update in the database
    retrieved_budget = get_budget(created_budget.id, sessionmaker=sessionmaker_test)
    assert isinstance(retrieved_budget, Budget)
    assert retrieved_budget.category_id == 2
    assert retrieved_budget.amount == 1500.00


def test_delete_budget(sessionmaker_test, sample_budget_base):
    created_budget = create_budget(sample_budget_base, sessionmaker=sessionmaker_test)

    delete_budget(created_budget.id, sessionmaker=sessionmaker_test)

    retrieved_budget = get_budget(created_budget.id, sessionmaker=sessionmaker_test)
    assert retrieved_budget is None


def test_get_nonexistent_budget(sessionmaker_test):
    non_existent_id = uuid4()
    retrieved_budget = get_budget(non_existent_id, sessionmaker=sessionmaker_test)
    assert retrieved_budget is None


def test_get_budgets_by_user_id_no_budgets(sessionmaker_test):
    user_id = uuid4()
    retrieved_budgets = get_budgets_by_user_id(user_id, sessionmaker=sessionmaker_test)
    assert retrieved_budgets == []
