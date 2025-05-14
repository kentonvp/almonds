from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy.orm import sessionmaker as sessionmaker_
from sqlalchemy.sql import delete, select

from almonds.db.database import SessionLocal
from almonds.models.plaid_item import PlaidItem as PlaidItemModel
from almonds.schemas.plaid_item import PlaidItem, PlaidItemBase


def create_item(
    item: PlaidItemBase, *, sessionmaker: sessionmaker_ = SessionLocal
) -> PlaidItem:
    created_item = PlaidItem(
        id=uuid4(), created_at=datetime.utcnow(), expired=False, **item.model_dump()
    )
    model = PlaidItemModel(
        id=created_item.id,
        user_id=created_item.user_id,
        access_token=created_item.access_token,
        item_id=created_item.item_id,
        created_at=created_item.created_at,
        expired=created_item.expired,
    )

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


def delete_item(id: UUID, *, sessionmaker: sessionmaker_ = SessionLocal) -> None:
    with sessionmaker() as session:
        stmt = delete(PlaidItemModel).where(PlaidItemModel.id == id)
        session.execute(stmt)
        session.commit()
