from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, SecretStr


class UserBase(BaseModel):
    username: str
    email: EmailStr
    password: SecretStr


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    last_updated: datetime
