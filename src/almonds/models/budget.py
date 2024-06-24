from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Date, Integer, Numeric

from almonds.db.database import Base
from almonds.models.constants import MAX_DOLLAR_DIGITS


class Budget(Base):
    __tablename__ = "budgets"

    budget_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    amount = Column(Numeric(MAX_DOLLAR_DIGITS, 2), nullable=False)
    start_date = Column(Date, nullable=False)
