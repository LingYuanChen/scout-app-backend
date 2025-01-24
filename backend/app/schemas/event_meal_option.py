from enum import Enum
from uuid import UUID

from sqlmodel import Field, SQLModel


# Enums
class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    LATE_NIGHT = "late_night"


class EventMealOptionCreateBase(SQLModel):
    meal_id: UUID = Field(foreign_key="meal.id")
    meal_type: MealType
    day: int
    max_quantity: int | None = None


# Event Meal Option models
class EventMealOptionCreate(EventMealOptionCreateBase):
    pass
