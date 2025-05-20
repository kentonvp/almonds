from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import UUID, Boolean, DateTime, String

from almonds.db.database import Base


class PlaidItem(Base):
    __tablename__ = "plaid_items"

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    access_token = Column(String, nullable=False)
    item_id = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    expired = Column(Boolean, nullable=False)
    cursor = Column(String(length=256), nullable=True)
    synced_at = Column(DateTime, nullable=True)
