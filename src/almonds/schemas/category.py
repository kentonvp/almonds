from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    name: str
    user_id: UUID | None


class Category(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
