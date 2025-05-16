from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TransactionBase(BaseModel):
    user_id: UUID
    category_id: int
    amount: float
    description: str
    datetime: datetime
    pending: bool
    item_id: UUID | None


class Transaction(TransactionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
