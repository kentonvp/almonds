from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import UUID, String

from almonds.db.database import Base


class PlaidTransaction(Base):
    __tablename__ = "plaid_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True)
    account_id = Column(String, ForeignKey("plaid_accounts.id"), nullable=False)
    transaction_id = Column(String, ForeignKey("users.id"), nullable=False)
