from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import UUID, DateTime, String

from almonds.db.database import Base


class Request(Base):
    __tablename__ = "plaid_requests"

    id = Column(UUID(as_uuid=True), primary_key=True)
    request_id = Column(String, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    call = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
