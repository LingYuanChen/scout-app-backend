from uuid import UUID

from sqlmodel import Field, SQLModel


class MealChoiceCreateBase(SQLModel):
    attendance_id: UUID = Field(foreign_key="attendance.id")
    event_meal_option_id: UUID = Field(foreign_key="eventmealoption.id")
    quantity: int = 1
    notes: str | None = None


class MealChoiceCreate(MealChoiceCreateBase):
    pass


class MealChoiceUpdate(SQLModel):
    event_meal_option_id: UUID | None = None
    quantity: int | None = None
    notes: str | None = None
