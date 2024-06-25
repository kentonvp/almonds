from uuid import UUID, uuid4

from sqlalchemy.orm import sessionmaker as sessionmaker_
from sqlalchemy.sql import delete, select, update

from almonds.db.database import SessionLocal
from almonds.models.budget import Budget as BudgetModel
from almonds.schemas.budget import Budget, BudgetBase


def create_budget(
    budget: BudgetBase, *, sessionmaker: sessionmaker_ = SessionLocal
) -> Budget:
    created_budget = Budget(id=uuid4(), **budget.model_dump())

    model = BudgetModel(**created_budget.model_dump())

    with sessionmaker() as session:
        session.add(model)
        session.commit()

    return created_budget


def get_budget(
    budget_id: UUID, *, sessionmaker: sessionmaker_ = SessionLocal
) -> Budget | None:
    with sessionmaker() as session:
        stmt = select(BudgetModel).where(BudgetModel.id == budget_id)
        budget = session.scalars(stmt).first()

    if not budget:
        return None

    return Budget.model_validate(budget)


def get_budgets_by_user_id(
    user_id: UUID, *, sessionmaker: sessionmaker_ = SessionLocal
) -> list[Budget]:
    with sessionmaker() as session:
        stmt = select(BudgetModel).where(BudgetModel.user_id == user_id)
        budgets = session.scalars(stmt).all()

    if not budgets:
        return []

    return [Budget.model_validate(b) for b in budgets]


def update_budget(
    budget: Budget, *, sessionmaker: sessionmaker_ = SessionLocal
) -> Budget:
    with sessionmaker() as session:
        stmt = (
            update(BudgetModel)
            .where(BudgetModel.id == budget.id)
            .values(**budget.model_dump())
        )
        session.execute(stmt)
        session.commit()

    return budget


def delete_budget(budget_id: UUID, *, sessionmaker: sessionmaker_ = SessionLocal):
    with sessionmaker() as session:
        stmt = delete(BudgetModel).where(BudgetModel.id == budget_id)
        session.execute(stmt)
        session.commit()
