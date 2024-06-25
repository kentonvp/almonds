import datetime
from datetime import timedelta
from uuid import UUID, uuid4

import pydantic
import pytest

# Import the functions to be tested
from almonds.crud.goal import (
    create_goal,
    delete_goal,
    get_goal_by_id,
    get_goals_by_user,
    update_goal,
)
from almonds.models.goal import Goal as GoalModel
from almonds.schemas.goal import Goal, GoalBase, GoalUpdate


@pytest.fixture
def sample_goal_base():
    return GoalBase(
        user_id=uuid4(),
        name="Test Goal",
        target_amount=1000.00,
        current_amount=0.00,
        deadline=datetime.date.today() + timedelta(days=30),
        status="In Progress",
    )


def test_create_goal(sessionmaker_test, sample_goal_base):
    created_goal = create_goal(sample_goal_base, sessionmaker=sessionmaker_test)

    assert isinstance(created_goal, Goal)
    assert isinstance(created_goal.id, UUID)
    assert created_goal.name == sample_goal_base.name
    assert created_goal.target_amount == sample_goal_base.target_amount
    assert created_goal.current_amount == sample_goal_base.current_amount
    assert created_goal.deadline == sample_goal_base.deadline
    assert created_goal.user_id == sample_goal_base.user_id


def test_get_goal_by_id(sessionmaker_test, sample_goal_base):
    created_goal = create_goal(sample_goal_base, sessionmaker=sessionmaker_test)

    retrieved_goal = get_goal_by_id(created_goal.id, sessionmaker=sessionmaker_test)

    assert retrieved_goal is not None
    assert retrieved_goal.id == created_goal.id
    assert retrieved_goal.name == created_goal.name
    assert retrieved_goal.target_amount == created_goal.target_amount
    assert retrieved_goal.current_amount == created_goal.current_amount
    assert retrieved_goal.deadline == created_goal.deadline
    assert retrieved_goal.user_id == created_goal.user_id


def test_get_goals_by_user(sessionmaker_test, sample_goal_base):
    created_goal1 = create_goal(sample_goal_base, sessionmaker=sessionmaker_test)
    created_goal2 = create_goal(sample_goal_base, sessionmaker=sessionmaker_test)

    retrieved_goals = get_goals_by_user(
        sample_goal_base.user_id, sessionmaker=sessionmaker_test
    )

    assert len(retrieved_goals) == 2
    assert any(g.id == created_goal1.id for g in retrieved_goals)
    assert any(g.id == created_goal2.id for g in retrieved_goals)


def test_update_goal(sessionmaker_test, sample_goal_base):
    created_goal = create_goal(sample_goal_base, sessionmaker=sessionmaker_test)

    updated_goal = GoalUpdate(
        **(
            created_goal.model_dump()
            | {"name": "Updated Goal", "current_amount": 500.00}
        )
    )

    result = update_goal(updated_goal, sessionmaker=sessionmaker_test)

    assert result.name == "Updated Goal"
    assert result.current_amount == 500.00
    assert result.last_updated > created_goal.last_updated

    # Verify the update in the database
    retrieved_goal = get_goal_by_id(created_goal.id, sessionmaker=sessionmaker_test)
    assert isinstance(retrieved_goal, Goal)
    assert retrieved_goal.name == "Updated Goal"
    assert retrieved_goal.current_amount == 500.00


def test_delete_goal(sessionmaker_test, sample_goal_base):
    created_goal = create_goal(sample_goal_base, sessionmaker=sessionmaker_test)

    delete_goal(created_goal.id, sessionmaker=sessionmaker_test)

    retrieved_goal = get_goal_by_id(created_goal.id, sessionmaker=sessionmaker_test)
    assert retrieved_goal is None


def test_get_nonexistent_goal(sessionmaker_test):
    non_existent_id = uuid4()
    retrieved_goal = get_goal_by_id(non_existent_id, sessionmaker=sessionmaker_test)
    assert retrieved_goal is None


def test_get_goals_by_user_no_goals(sessionmaker_test):
    user_id = uuid4()
    retrieved_goals = get_goals_by_user(user_id, sessionmaker=sessionmaker_test)
    assert retrieved_goals == []


def test_update_nonexistent_goal(sessionmaker_test, sample_goal_base):
    non_existent_goal = GoalUpdate(id=uuid4(), **sample_goal_base.model_dump())

    with pytest.raises(pydantic.ValidationError):
        update_goal(non_existent_goal, sessionmaker=sessionmaker_test)


def test_delete_nonexistent_goal(sessionmaker_test):
    non_existent_id = uuid4()

    # This should not raise an exception
    delete_goal(non_existent_id, sessionmaker=sessionmaker_test)
