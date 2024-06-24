from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

from almonds.db.database import Base
from almonds.models.constants import MAX_CATEGORY_NAME_LENGTH


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(MAX_CATEGORY_NAME_LENGTH))
