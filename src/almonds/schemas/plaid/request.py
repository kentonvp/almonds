from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RequestBase(BaseModel):
    request_id: str
    user_id: UUID
    call: str


class Request(RequestBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
