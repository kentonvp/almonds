import json
from uuid import UUID

from sqlalchemy.orm import sessionmaker as sessionmaker_
from sqlalchemy.sql import select, update

from almonds.db.database import SessionLocal
from almonds.models.user_settings import UserSetting as UserSettingModel
from almonds.schemas.user_settings import UserSetting


def default_settings() -> dict:
    return {"expected_income": None}


def dump(settings: dict) -> str:
    return json.dumps(settings)


def parse(settings: str) -> dict:
    return json.loads(settings)


def create_default_user_settings(
    user_id: UUID, *, sessionmaker: sessionmaker_ = SessionLocal
) -> dict:
    d_settings = default_settings()
    model = UserSettingModel(user_id=user_id, dictionary=dump(d_settings))

    with sessionmaker() as session:
        session.add(model)
        session.commit()

    return d_settings


def get_user_settings(
    user_id: UUID, *, sessionmaker: sessionmaker_ = SessionLocal
) -> dict:
    with sessionmaker() as session:
        stmt = select(UserSettingModel).where(UserSettingModel.user_id == user_id)
        settings = session.scalar(stmt)

    if not settings:
        return create_default_user_settings(user_id, sessionmaker=sessionmaker)

    settings = UserSetting.model_validate(settings)
    return parse(settings.dictionary)


def write_user_settings(
    user_id: UUID, settings: dict, *, sessionmaker: sessionmaker_ = SessionLocal
):
    with sessionmaker() as session:
        stmt = (
            update(UserSettingModel)
            .where(UserSettingModel.user_id == user_id)
            .values(dictionary=dump(settings))
        )
        session.execute(stmt)
        session.commit()


def update_user_settings(
    user_id: UUID, updates: dict, *, sessionmaker: sessionmaker_ = SessionLocal
) -> dict:
    old_settings = get_user_settings(user_id, sessionmaker=sessionmaker)

    new_settings = old_settings | updates
    write_user_settings(user_id, new_settings, sessionmaker=sessionmaker)

    return new_settings


def remove_user_settings(
    user_id: UUID, keys: list, *, sessionmaker: sessionmaker_ = SessionLocal
) -> dict:
    settings = get_user_settings(user_id, sessionmaker=sessionmaker)

    for k in keys:
        del settings[k]

    write_user_settings(user_id, settings, sessionmaker=sessionmaker)

    return settings
