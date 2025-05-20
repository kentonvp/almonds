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
        last_logged_in=datetime.utcnow(),
        **user.model_dump(),
    )
    model = UserModel(
        id=created_user.id,
        created_at=created_user.created_at,
        last_updated=created_user.last_updated,
        last_logged_in=created_user.last_logged_in,
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


def mark_logged_in(
    user_id: UUID, *, sessionmaker: sessionmaker_ = SessionLocal
) -> None:
    with sessionmaker() as session:
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(last_logged_in=datetime.utcnow())
            .returning(UserModel)
        )
        session.scalars(stmt).first()
        session.commit()


def most_recently_logged_in(
    limit: int = 10, *, sessionmaker: sessionmaker_ = SessionLocal
) -> list[User]:
    with sessionmaker() as session:
        stmt = select(UserModel).order_by(UserModel.last_logged_in.desc()).limit(limit)
        users = session.scalars(stmt).all()

    return [User.model_validate(user) for user in users]
