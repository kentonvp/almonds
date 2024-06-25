from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import UUID, DateTime, Integer, Numeric, String

from almonds.db.database import Base
from almonds.models.constants import (
    MAX_DESCRIPTION_LENGTH,
    MAX_DOLLAR_DIGITS,
    MAX_TRANSACTION_NAME_LENGTH,
)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    amount = Column(Numeric(MAX_DOLLAR_DIGITS, 2), nullable=False)
    description = Column(String(MAX_DESCRIPTION_LENGTH))
    datetime = Column(DateTime, nullable=False)
