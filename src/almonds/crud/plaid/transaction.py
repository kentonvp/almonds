from uuid import UUID, uuid4

from sqlalchemy.orm import sessionmaker as sessionmaker_
from sqlalchemy.sql import delete, select

from almonds.db.database import SessionLocal
from almonds.models.plaid.transaction import PlaidTransaction as PlaidTransactionModel
from almonds.schemas.plaid.transaction import PlaidTransaction, PlaidTransactionBase


def create_transaction(
    transaction: PlaidTransactionBase, *, sessionmaker: sessionmaker_ = SessionLocal
) -> PlaidTransaction:
    created_transaction = PlaidTransaction(
        id=uuid4(),
        **transaction.model_dump(),
    )

    with sessionmaker() as session:
        model = PlaidTransactionModel(**created_transaction.model_dump())
        session.add(model)
        session.commit()

    return created_transaction


def get_transaction(
    transaction_id: UUID, *, sessionmaker: sessionmaker_ = SessionLocal
) -> PlaidTransaction:
    with sessionmaker() as session:
        stmt = select(PlaidTransactionModel).where(
            PlaidTransactionModel.id == transaction_id
        )
        transaction = session.scalars(stmt).first()

    if not transaction:
        return None

    return PlaidTransaction.model_validate(transaction)


def get_transaction_by_plaid_id(
    plaid_id: str, *, sessionmaker: sessionmaker_ = SessionLocal
) -> PlaidTransaction:
    with sessionmaker() as session:
        stmt = select(PlaidTransactionModel).where(
            PlaidTransactionModel.transaction_id == plaid_id
        )
        transaction = session.scalars(stmt).first()

    if not transaction:
        return None

    return PlaidTransaction.model_validate(transaction)


def delete_transaction(
    transaction_id: UUID, *, sessionmaker: sessionmaker_ = SessionLocal
) -> None:
    with sessionmaker() as session:
        stmt = delete(PlaidTransactionModel).where(
            PlaidTransactionModel.id == transaction_id
        )
        session.execute(stmt)
        session.commit()
