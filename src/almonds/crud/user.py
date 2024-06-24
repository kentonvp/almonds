from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import delete, select, update

from almonds.db.database import SessionLocal
from almonds.models.user import User as UserModel
from almonds.schemas.user import User, UserBase


def create_user(user: UserBase) -> User:
    created_user = User(
        id=uuid4(),
        created_at=datetime.utcnow(),
        last_updated=datetime.utcnow(),
        **user.dict()
    )
    model = UserModel(
        id=created_user.id,
        created_at=created_user.created_at,
        last_updated=created_user.last_updated,
        email=created_user.email,
        username=created_user.username,
        password=created_user.password.get_secret_value(),
    )

    with SessionLocal() as session:
        session.add(model)
        session.commit()

    return created_user


def get_user_by_id(user_id: UUID) -> User | None:
    with SessionLocal() as session:
        stmt = select(UserModel).where(UserModel.id == user_id)
        user = session.scalars(stmt).first()

    if user is not None:
        return User.from_orm(user)
    return None


def get_user_by_username(username: str) -> User | None:
    with SessionLocal() as session:
        stmt = select(UserModel).where(UserModel.username == username)
        user = session.scalars(stmt).first()

    if user is not None:
        return User.from_orm(user)
    return None


def update_user(user: User) -> User:
    user.last_updated = datetime.utcnow()

    with SessionLocal() as session:
        stmt = update(UserModel).where(UserModel.id == user.id).values(**user.dict())
        session.execute(stmt)
        session.commit()

    return user


def delete_user(user_id: UUID):
    with SessionLocal() as session:
        stmt = delete(UserModel).where(UserModel.id == user_id)
        session.execute(stmt)
        session.commit()
