from uuid import UUID, uuid4

from sqlalchemy.orm import sessionmaker as sessionmaker_
from sqlalchemy.sql import delete, select, update

from almonds.db.database import SessionLocal
from almonds.models.plaid.account import PlaidAccount as PlaidAccountModel
from almonds.schemas.plaid.account import PlaidAccount, PlaidAccountBase


def create_account(
    account: PlaidAccountBase, *, sessionmaker: sessionmaker_ = SessionLocal
) -> PlaidAccount:
    created_account = PlaidAccount(
        id=uuid4(),
        **account.model_dump(),
    )

    with sessionmaker() as session:
        model = PlaidAccountModel(**created_account.model_dump())
        session.add(model)
        session.commit()

    return created_account


def get_account(
    account_id: UUID, *, sessionmaker: sessionmaker_ = SessionLocal
) -> PlaidAccount | None:
    with sessionmaker() as session:
        stmt = select(PlaidAccountModel).where(PlaidAccountModel.id == account_id)
        account = session.scalars(stmt).first()

    if not account:
        return None

    return PlaidAccount.model_validate(account)


def get_account_by_plaid_id(
    plaid_id: str, *, sessionmaker: sessionmaker_ = SessionLocal
) -> PlaidAccount | None:
    with sessionmaker() as session:
        stmt = select(PlaidAccountModel).where(PlaidAccountModel.account_id == plaid_id)
        account = session.scalars(stmt).first()

    if not account:
        return None

    return PlaidAccount.model_validate(account)


def update_account(
    account: PlaidAccount, *, sessionmaker: sessionmaker_ = SessionLocal
) -> PlaidAccount:
    with sessionmaker() as session:
        stmt = (
            update(PlaidAccountModel)
            .where(PlaidAccountModel.id == account.id)
            .values(**account.model_dump())
        )

        session.execute(stmt)
        session.commit()

    return account


def delete_account(
    account_id: UUID, *, sessionmaker: sessionmaker_ = SessionLocal
) -> None:
    with sessionmaker() as session:
        stmt = delete(PlaidAccountModel).where(PlaidAccountModel.id == account_id)
        session.execute(stmt)
        session.commit()
