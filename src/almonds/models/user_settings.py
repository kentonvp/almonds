from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import UUID, String

from almonds.db.database import Base


class UserSetting(Base):
    __tablename__ = "user_settings"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    dictionary = Column(String, nullable=False)
