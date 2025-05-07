from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy.orm import sessionmaker as sessionmaker_
from sqlalchemy.sql import delete, select, update

from almonds.db.database import SessionLocal
from almonds.models.user import User as UserModel
from almonds.schemas.user import User, UserBase, UserUpdate


def create_user(user: UserBase, *, sessionmaker: sessionmaker_ = SessionLocal) -> User:
    created_user = User(
        id=uuid4(),
        created_at=datetime.utcnow(),
        last_updated=datetime.utcnow(),
        **user.model_dump(),
    )
    model = UserModel(
        id=created_user.id,
        created_at=created_user.created_at,
        last_updated=created_user.last_updated,
        email=created_user.email,
        username=created_user.username,
        password=created_user.password.get_secret_value(),
    )

    with sessionmaker() as session:
        session.add(model)
        session.commit()

    return created_user


def get_user_by_id(
    user_id: UUID, *, sessionmaker: sessionmaker_ = SessionLocal
) -> User | None:
    with sessionmaker() as session:
        stmt = select(UserModel).where(UserModel.id == user_id)
        user = session.scalars(stmt).first()

    if not user:
        return None

    return User.model_validate(user)


def get_user_by_username(
    username: str, *, sessionmaker: sessionmaker_ = SessionLocal
) -> User | None:
    with sessionmaker() as session:
        stmt = select(UserModel).where(UserModel.username == username)
        user = session.scalars(stmt).first()

    if not user:
        return None

    return User.model_validate(user)


def update_user(
    user_update: UserUpdate, *, sessionmaker: sessionmaker_ = SessionLocal
) -> User:
    with sessionmaker() as session:
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_update.id)
            .values(
                username=user_update.username,
                email=user_update.email,
                password=user_update.password.get_secret_value(),
                last_updated=datetime.utcnow(),
            )
            .returning(UserModel)
        )
        updated_user = session.scalars(stmt).first()
        session.commit()

        user = User.model_validate(updated_user)

    return user


def delete_user(user_id: UUID, *, sessionmaker: sessionmaker_ = SessionLocal):
    with sessionmaker() as session:
        stmt = delete(UserModel).where(UserModel.id == user_id)
        session.execute(stmt)
        session.commit()
