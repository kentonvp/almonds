from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy.orm import sessionmaker as sessionmaker_
from sqlalchemy.sql import delete, select, update

from almonds.db.database import SessionLocal
from almonds.models.transaction import Transaction as TransactionModel
from almonds.schemas.transaction import Transaction, TransactionBase


def create_transaction(
    transaction: TransactionBase, *, sessionmaker: sessionmaker_ = SessionLocal
) -> Transaction:
    created_transaction = Transaction(id=uuid4(), **transaction.dict())

    model = TransactionModel(**created_transaction.dict())

    with sessionmaker() as session:
        session.add(model)
        session.commit()

    return created_transaction


def get_transaction_by_id(
    transaction_id: UUID, *, sessionmaker: sessionmaker_ = SessionLocal
) -> Transaction | None:
    with sessionmaker() as session:
        stmt = select(TransactionModel).where(TransactionModel.id == transaction_id)
        transaction = session.scalars(stmt).first()

    if not transaction:
        return None

    return Transaction.from_orm(transaction)


def get_transactions_by_user(
    user_id: UUID, *, sessionmaker: sessionmaker_ = SessionLocal
) -> list[Transaction]:
    with sessionmaker() as session:
        stmt = select(TransactionModel).where(TransactionModel.user_id == user_id)
        transactions = session.scalars(stmt).all()

    if not transactions:
        return []

    return [Transaction.from_orm(tx) for tx in transactions]


def update_transaction(
    transaction: Transaction, *, sessionmaker: sessionmaker_ = SessionLocal
) -> Transaction:
    with sessionmaker() as session:
        stmt = (
            update(TransactionModel)
            .where(TransactionModel.id == transaction.id)
            .values(**transaction.dict())
        )
        session.execute(stmt)
        session.commit()

    return transaction
