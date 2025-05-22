from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import UUID, Numeric, String

from almonds.db.database import Base
from almonds.models.constants import MAX_DOLLAR_DIGITS


class PlaidAccount(Base):
    __tablename__ = "plaid_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    account_id = Column(String, nullable=False)
    balance = Column(Numeric(MAX_DOLLAR_DIGITS, 2), nullable=False)
    cursor = Column(String, nullable=True)
