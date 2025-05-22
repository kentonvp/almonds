from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PlaidTransactionBase(BaseModel):
    user_id: UUID
    account_id: str
    transaction_id: str


class PlaidTransaction(PlaidTransactionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
