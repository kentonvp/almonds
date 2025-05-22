import datetime
from uuid import UUID, uuid4

from sqlalchemy.orm import sessionmaker as sessionmaker_
from sqlalchemy.sql import select

from almonds.db.database import SessionLocal
from almonds.models.plaid.request import Request as RequestModel
from almonds.schemas.plaid.request import Request, RequestBase


def create_request(
    request: RequestBase, *, sessionmaker: sessionmaker_ = SessionLocal
) -> Request:
    created_log = Request(
        id=uuid4(),
        created_at=datetime.datetime.utcnow(),
        **request.model_dump(),
    )

    with sessionmaker() as session:
        model = RequestModel(**created_log.model_dump())
        session.add(model)
        session.commit()

    return created_log


def get_requests_by_user_id(
    user_id: UUID, *, sessionmaker: sessionmaker_ = SessionLocal
) -> list[Request]:
    with sessionmaker() as session:
        stmt = (
            select(RequestModel)
            .where(RequestModel.user_id == user_id)
            .order_by(RequestModel.created_at.desc())
        )
        logs = session.scalars(stmt).all()

    return [Request.model_validate(log) for log in logs]
