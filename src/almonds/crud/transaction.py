import datetime
from uuid import UUID, uuid4

from sqlalchemy.orm import sessionmaker as sessionmaker_
from sqlalchemy.sql import extract, select, update

from almonds.db.database import SessionLocal
from almonds.models.transaction import Transaction as TransactionModel
from almonds.schemas.transaction import Transaction, TransactionBase


def create_transaction(
    transaction: TransactionBase, *, sessionmaker: sessionmaker_ = SessionLocal
) -> Transaction:
    created_transaction = Transaction(id=uuid4(), **transaction.model_dump())

    model = TransactionModel(**created_transaction.model_dump())

    with sessionmaker() as session:
        session.add(model)
        session.commit()

    return created_transaction


def count_transactions(
    user_id: UUID, *, sessionmaker: sessionmaker_ = SessionLocal
) -> int:
    with sessionmaker() as session:
        count = (
            session.query(TransactionModel)
            .where(TransactionModel.user_id == user_id)
            .count()
        )

    return count


def get_transaction_by_id(
    transaction_id: UUID, *, sessionmaker: sessionmaker_ = SessionLocal
) -> Transaction | None:
    with sessionmaker() as session:
        stmt = select(TransactionModel).where(TransactionModel.id == transaction_id)
        transaction = session.scalars(stmt).first()

    if not transaction:
        return None

    return Transaction.model_validate(transaction)


def get_transactions_by_user(
    user_id: UUID,
    *,
    limit: int = 500,
    offset=0,
    sessionmaker: sessionmaker_ = SessionLocal
) -> list[Transaction]:
    with sessionmaker() as session:
        stmt = (
            select(TransactionModel)
            .where(TransactionModel.user_id == user_id)
            .order_by(TransactionModel.datetime.desc())
            .limit(limit)
            .offset(offset)
        )
        transactions = session.scalars(stmt).all()

    if not transactions:
        return []

    return [Transaction.model_validate(tx) for tx in transactions]


def update_transaction(
    transaction: Transaction, *, sessionmaker: sessionmaker_ = SessionLocal
) -> Transaction:
    with sessionmaker() as session:
        stmt = (
            update(TransactionModel)
            .where(TransactionModel.id == transaction.id)
            .values(**transaction.model_dump())
            .returning(TransactionModel)
        )
        transaction_ = session.scalars(stmt).first()
        session.commit()

        transaction = Transaction.model_validate(transaction_)

    return transaction


def delete_transaction(
    transaction_id: UUID, *, sessionmaker: sessionmaker_ = SessionLocal
) -> None:
    with sessionmaker() as session:
        stmt = select(TransactionModel).where(TransactionModel.id == transaction_id)
        transaction = session.scalars(stmt).first()

        if not transaction:
            return

        session.delete(transaction)
        session.commit()


def get_transactions_by_month(
    user_id: UUID,
    today: datetime.date = None,
    *,
    sessionmaker: sessionmaker_ = SessionLocal
) -> list[Transaction]:
    if today is None:
        # For testing purposes, we allow to pass a specific date
        today = datetime.date.today()

    with sessionmaker() as session:
        stmt = select(TransactionModel).where(
            TransactionModel.user_id == user_id,
            extract("month", TransactionModel.datetime) == today.month,
            extract("year", TransactionModel.datetime) == today.year,
        )
        transactions = session.scalars(stmt).all()

    return [Transaction.model_validate(tx) for tx in transactions]


def count_transactions_by_month(
    user_id: UUID,
    today: datetime.date = None,
    *,
    sessionmaker: sessionmaker_ = SessionLocal
) -> int:
    if today is None:
        # For testing purposes, we allow to pass a specific date
        today = datetime.date.today()

    with sessionmaker() as session:
        count = (
            session.query(TransactionModel)
            .where(
                TransactionModel.user_id == user_id,
                extract("month", TransactionModel.datetime) == today.month,
                extract("year", TransactionModel.datetime) == today.year,
            )
            .count()
        )

    return count
