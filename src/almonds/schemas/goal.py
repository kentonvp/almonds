from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, SecretStr


class GoalBase(BaseModel):
    user_id: UUID
    name: str
    target_amount: float
    current_amount: float
    deadline: date
    status: str


class GoalUpdate(GoalBase):
    id: UUID


class Goal(GoalUpdate):
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime
    last_updated: datetime
