from uuid import uuid4

from sqlalchemy.orm import sessionmaker as sessionmaker_
from sqlalchemy.sql import delete, select, update

from almonds.db.database import SessionLocal
from almonds.models.category import Category as CategoryModel
from almonds.schemas.category import Category, CategoryBase


def create_category(
    category: CategoryBase, *, sessionmaker: sessionmaker_ = SessionLocal
) -> Category:

    model = CategoryModel(name=category.name)

    with sessionmaker() as session:
        session.add(model)
        session.commit()

        created_category = Category.model_validate(model)

    return created_category


def get_category_by_name(
    name: str, *, sessionmaker: sessionmaker_ = SessionLocal
) -> Category | None:
    with sessionmaker() as session:
        stmt = select(CategoryModel).where(CategoryModel.name == name)
        category = session.scalars(stmt).first()

    if not category:
        return None

    return Category.model_validate(category)


def delete_category(category_id: int, *, sessionmaker: sessionmaker_ = SessionLocal):
    with sessionmaker() as session:
        stmt = delete(CategoryModel).where(CategoryModel.id == category_id)
        session.execute(stmt)
        session.commit()
