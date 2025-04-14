from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import UUID, Boolean, DateTime, String

from almonds.db.database import Base
from almonds.models.constants import MAX_PASSWORD_HASH_LENGTH


class PlaidItem(Base):
    __tablename__ = "plaid_items"

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    access_token = Column(String(MAX_PASSWORD_HASH_LENGTH), nullable=False)
    item_id = Column(String(), nullable=False)
    created_at = Column(DateTime, nullable=False)
    expired = Column(Boolean, nullable=False)
