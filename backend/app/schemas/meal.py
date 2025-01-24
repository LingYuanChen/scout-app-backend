from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel


class MealBase(SQLModel):
    name: str
    description: str | None = None
    price: float | None = None
    is_vegetarian: bool = False
    is_beef: bool = False
    calories: int | None = None


class MealCreate(MealBase):
    pass


class MealUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    is_vegetarian: bool | None = None
    is_beef: bool | None = None
    calories: int | None = None


class MealPublic(MealBase):
    id: UUID
    created_at: datetime
    created_by_id: UUID
