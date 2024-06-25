from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import UUID, Date, Integer, Numeric

from almonds.db.database import Base
from almonds.models.constants import MAX_DOLLAR_DIGITS


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    amount = Column(Numeric(MAX_DOLLAR_DIGITS, 2), nullable=False)
    start_date = Column(Date, nullable=False)
