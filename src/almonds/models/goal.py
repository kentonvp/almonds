from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import UUID, Date, DateTime, Numeric, String

from almonds.db.database import Base
from almonds.models.constants import (
    MAX_DOLLAR_DIGITS,
    MAX_GOAL_NAME_LENGTH,
    MAX_STATUS_LENGTH,
)


class Goal(Base):
    __tablename__ = "goals"

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    name = Column(String(MAX_GOAL_NAME_LENGTH), nullable=False)
    target_amount = Column(Numeric(MAX_DOLLAR_DIGITS, 2), nullable=False)
    current_amount = Column(Numeric(MAX_DOLLAR_DIGITS, 2), default=0.0)
    deadline = Column(Date)
    status = Column(String(MAX_STATUS_LENGTH))
    created_at = Column(DateTime)
    last_updated = Column(DateTime)
