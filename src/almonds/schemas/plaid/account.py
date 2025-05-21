from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PlaidAccountBase(BaseModel):
    user_id: UUID
    account_id: str
    balance: float
    cursor: str | None


class PlaidAccount(PlaidAccountBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
