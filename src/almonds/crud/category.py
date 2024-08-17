from uuid import UUID

from sqlalchemy.orm import sessionmaker as sessionmaker_
from sqlalchemy.sql import delete, select, update

from almonds.db.database import SessionLocal
from almonds.models.category import Category as CategoryModel
from almonds.schemas.category import Category, CategoryBase


def create_category(
    category: CategoryBase, *, sessionmaker: sessionmaker_ = SessionLocal
) -> Category:

    model = CategoryModel(name=category.name, user_id=category.user_id)

    with sessionmaker() as session:
        session.add(model)
        session.commit()

        created_category = Category.model_validate(model)

    return created_category


def get_category_by_id(
    category_id: int, *, sessionmaker: sessionmaker_ = SessionLocal
) -> Category | None:
    with sessionmaker() as session:
        stmt = select(CategoryModel).where(CategoryModel.id == category_id)
        category = session.scalar(stmt)

    if not category:
        return None

    return Category.model_validate(category)


def get_default_categories(
    *, sessionmaker: sessionmaker_ = SessionLocal
) -> list[Category]:
    with sessionmaker() as session:
        stmt = select(CategoryModel).where(CategoryModel.user_id == None)
        categories = session.scalars(stmt).all()

    return [Category.model_validate(c) for c in categories]


def get_categories_by_user(
    user_id: UUID, *, sessionmaker: sessionmaker_ = SessionLocal
) -> list[Category]:
    with sessionmaker() as session:
        stmt = select(CategoryModel).where(CategoryModel.user_id == user_id)
        categories = session.scalars(stmt).all()

    defaults = get_default_categories(sessionmaker=sessionmaker)
    if not categories:
        return defaults

    return [Category.model_validate(c) for c in categories] + defaults


def update_category(
    category: Category, *, sessionmaker: sessionmaker_ = SessionLocal
) -> Category:
    with sessionmaker() as session:
        stmt = (
            update(CategoryModel)
            .where(CategoryModel.id == category.id)
            .values(name=category.name)
        )
        session.execute(stmt)
        session.commit()

    return category


def delete_category(category_id: int, *, sessionmaker: sessionmaker_ = SessionLocal):
    with sessionmaker() as session:
        stmt = delete(CategoryModel).where(CategoryModel.id == category_id)
        session.execute(stmt)
        session.commit()
