from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import UUID, Integer, String

from almonds.db.database import Base
from almonds.models.constants import MAX_CATEGORY_NAME_LENGTH


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    name = Column(String(MAX_CATEGORY_NAME_LENGTH), nullable=False)
