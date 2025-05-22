from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, SecretStr


class UserBase(BaseModel):
    username: str
    email: EmailStr
    password: SecretStr


class UserUpdate(UserBase):
    id: UUID


class User(UserUpdate):
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime
    last_updated: datetime
    last_logged_in: datetime
