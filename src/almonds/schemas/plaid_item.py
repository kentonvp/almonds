from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PlaidItemBase(BaseModel):
    user_id: UUID
    access_token: str
    item_id: str


class PlaidItem(PlaidItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    expired: bool
