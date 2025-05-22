from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy.orm import sessionmaker as sessionmaker_
from sqlalchemy.sql import select, update

from almonds.db.database import SessionLocal
from almonds.models.plaid.plaid_item import PlaidItem as PlaidItemModel
from almonds.schemas.plaid.plaid_item import PlaidItem, PlaidItemBase


def create_item(
    item: PlaidItemBase, *, sessionmaker: sessionmaker_ = SessionLocal
) -> PlaidItem:
    created_item = PlaidItem(
        id=uuid4(),
        created_at=datetime.utcnow(),
        expired=False,
        cursor=None,
        synced_at=None,
        **item.model_dump(),
    )
    model = PlaidItemModel(**created_item.model_dump())

    with sessionmaker() as session:
        session.add(model)
        session.commit()

    return created_item


def get_item(
    id: UUID, *, sessionmaker: sessionmaker_ = SessionLocal
) -> PlaidItem | None:
    with sessionmaker() as session:
        stmt = select(PlaidItemModel).where(PlaidItemModel.id == id)
        item = session.scalars(stmt).first()

    if not item:
        return None

    return PlaidItem.model_validate(item)


def get_items_for_user(
    user_id: UUID, *, sessionmaker: sessionmaker_ = SessionLocal
) -> list[PlaidItem]:
    with sessionmaker() as session:
        stmt = select(PlaidItemModel).where(PlaidItemModel.user_id == user_id)
        items = session.scalars(stmt).all()

    return [PlaidItem.model_validate(it) for it in items]


def get_active_items_for_user(
    user_id: UUID, *, sessionmaker: sessionmaker_ = SessionLocal
) -> list[PlaidItem]:
    with sessionmaker() as session:
        stmt = select(PlaidItemModel).where(
            PlaidItemModel.user_id == user_id, PlaidItemModel.expired == False  # noqa
        )
        items = session.scalars(stmt).all()

    return [PlaidItem.model_validate(it) for it in items]


def delete_item(id: UUID, *, sessionmaker: sessionmaker_ = SessionLocal) -> None:
    with sessionmaker() as session:
        stmt = (
            update(PlaidItemModel).where(PlaidItemModel.id == id).values(expired=True)
        )
        session.execute(stmt)
        session.commit()


def update_cursor(
    item_id: UUID, cursor: str | None, *, sessionmaker: sessionmaker_ = SessionLocal
) -> None:
    with sessionmaker() as session:
        stmt = (
            update(PlaidItemModel)
            .where(PlaidItemModel.id == item_id)
            .values(cursor=cursor, synced_at=datetime.utcnow())
        )
        session.execute(stmt)
        session.commit()
