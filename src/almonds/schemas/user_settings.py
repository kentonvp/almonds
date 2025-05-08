from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserSettingBase(BaseModel):
    user_id: UUID
    dictionary: str


class UserSetting(UserSettingBase):
    model_config = ConfigDict(from_attributes=True)
