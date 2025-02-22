import uuid
from datetime import datetime
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from .enums import MealType, RoleType


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str
    is_active: bool = True
    full_name: str | None = Field(default=None, max_length=255)
    role_type: RoleType = Field(default=RoleType.STUDENT)

    attendances: list["Attendance"] = Relationship(back_populates="user")
    coordinated_events: list["Event"] = Relationship(
        back_populates="coordinator",
        sa_relationship_kwargs={"foreign_keys": "[Event.coordinator_id]"},
    )


class Equipment(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    category: str = Field(default=None, max_length=100)
    location: str = Field(default=None, max_length=100)

    event_equipments: list["PackingEquipment"] = Relationship(
        back_populates="equipment"
    )


class Event(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    start_date: str = Field(max_length=10)  # Format: YYYY-MM-DD
    end_date: str = Field(max_length=10)
    coordinator_id: UUID = Field(foreign_key="user.id", nullable=True)

    coordinator: User = Relationship(
        back_populates="coordinated_events",
        sa_relationship_kwargs={"foreign_keys": "[Event.coordinator_id]"},
    )
    attendees: list["Attendance"] = Relationship(
        back_populates="event", cascade_delete=True
    )
    packing_equipments: list["PackingEquipment"] = Relationship(
        back_populates="event", cascade_delete=True
    )
    meal_options: list["EventMealOption"] = Relationship(
        back_populates="event", cascade_delete=True
    )


class Meal(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    restaurant: str
    description: str | None = None
    price: float | None = None
    is_vegetarian: bool = False
    is_beef: bool = False
    calories: int | None = None
    event_meal_options: list["EventMealOption"] = Relationship(back_populates="meal")


class EventMealOption(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    meal_id: UUID = Field(foreign_key="meal.id")
    event_id: UUID = Field(foreign_key="event.id")
    meal_type: MealType
    day: int
    max_quantity: int | None = None

    event: Event = Relationship(back_populates="meal_options")
    meal: Meal = Relationship(back_populates="event_meal_options")
    meal_choices: list["MealChoice"] = Relationship(back_populates="event_meal_option")


class PackingEquipment(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    event_id: UUID = Field(foreign_key="event.id", nullable=False)
    equipment_id: UUID = Field(foreign_key="equipment.id", nullable=False)
    quantity: int = Field(default=1)
    required: bool = Field(default=True)
    notes: str | None = Field(default=None, max_length=255)

    event: Event = Relationship(back_populates="packing_equipments")
    equipment: Equipment = Relationship(back_populates="event_equipments")


class MealChoice(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    attendance_id: UUID = Field(foreign_key="attendance.id")
    event_meal_option_id: UUID = Field(foreign_key="eventmealoption.id")
    quantity: int = 1
    notes: str | None = None

    attendance: "Attendance" = Relationship(back_populates="meal_choices")
    event_meal_option: EventMealOption = Relationship(back_populates="meal_choices")


class Attendance(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    event_id: UUID = Field(foreign_key="event.id", nullable=False)
    is_attending: bool = Field(default=True)

    user: User = Relationship(back_populates="attendances")
    event: Event = Relationship(back_populates="attendees")
    meal_choices: list[MealChoice] = Relationship(back_populates="attendance")


class Course(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    created_by_id: UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


__all__ = [
    "User",
    "Equipment",
    "Event",
    "Meal",
    "EventMealOption",
    "PackingEquipment",
    "MealChoice",
    "Attendance",
    "MealType",
    "Course",
]
