from sqlalchemy.schema import Column
from sqlalchemy.types import UUID, DateTime, String

from almonds.db.database import Base
from almonds.models.constants import (
    MAX_EMAIL_LENGTH,
    MAX_PASSWORD_HASH_LENGTH,
    MAX_USERNAME_LENGTH,
)


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True)
    username = Column(String(MAX_USERNAME_LENGTH), nullable=False)
    password = Column(String(MAX_PASSWORD_HASH_LENGTH), nullable=False)
    email = Column(String(MAX_EMAIL_LENGTH), nullable=False)
    created_at = Column(DateTime, nullable=False)
    last_updated = Column(DateTime, nullable=False)
