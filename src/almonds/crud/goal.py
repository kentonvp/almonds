from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy.orm import sessionmaker as sessionmaker_
from sqlalchemy.sql import delete, select, update

from almonds.db.database import SessionLocal
from almonds.models.goal import Goal as GoalModel
from almonds.schemas.goal import Goal, GoalBase


def create_goal(goal: GoalBase, *, sessionmaker: sessionmaker_ = SessionLocal) -> Goal:
    created_goal = Goal(id=uuid4(), **goal.dict())

    model = GoalModel(**created_goal.dict())
    with sessionmaker() as session:
        session.add(model)
        session.commit()

    return created_goal


def get_goal_by_id(
    goal_id: UUID, *, sessionmaker: sessionmaker_ = SessionLocal
) -> Goal | None:
    with sessionmaker() as session:
        stmt = select(GoalModel).where(GoalModel.id == goal_id)
        goal = session.scalars(stmt).first()

    if not goal:
        return None

    return Goal.from_orm(goal)


def get_goals_by_user(
    user_id: UUID, *, sessionmaker: sessionmaker_ = SessionLocal
) -> list[Goal]:
    with sessionmaker() as session:
        stmt = select(GoalModel).where(GoalModel.user_id == user_id)
        goals = session.scalars(stmt).all()

    if not goals:
        return []

    return [Goal.from_orm(g) for g in goals]


def update_goal(goal: Goal, *, sessionmaker: sessionmaker_ = SessionLocal) -> Goal:
    goal.last_updated = datetime.utcnow()

    with sessionmaker() as session:
        stmt = update(GoalModel).where(GoalModel.id == goal.id).values(**goal.dict())
        session.execute(stmt)
        session.commit()

    return goal


def delete_goal(goal_id: UUID, *, sessionmaker: sessionmaker_ = SessionLocal):
    with sessionmaker() as session:
        stmt = delete(GoalModel).where(GoalModel.id == goal_id)
        session.execute(stmt)
        session.commit()
