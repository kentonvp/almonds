from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BudgetBase(BaseModel):
    user_id: UUID
    category_id: int
    amount: float
    start_date: date


class Budget(BudgetBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
