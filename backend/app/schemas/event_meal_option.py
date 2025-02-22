from uuid import UUID

from sqlmodel import Field, SQLModel

from app.db.enums import MealType

from .meal import MealPublic


class EventMealOptionCreateBase(SQLModel):
    meal_id: UUID = Field(foreign_key="meal.id")
    meal_type: MealType
    day: int
    max_quantity: int | None = None


# Event Meal Option models
class EventMealOptionCreate(EventMealOptionCreateBase):
    pass


class EventMealOptionPublic(EventMealOptionCreateBase):
    id: UUID
    meal: MealPublic
