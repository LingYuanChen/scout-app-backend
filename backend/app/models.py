import uuid
from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


# Enums
class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    LATE_NIGHT = "late_night"


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    role: str = Field(default="student")  # "superuser", "teacher", "student"


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    attendances: list["Attendance"] = Relationship(back_populates="user")
    created_events: list["Event"] = Relationship(back_populates="created_by")


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties for Item (catalog)
class ItemBase(SQLModel):
    title: str = Field(
        min_length=1, max_length=255
    )  # Keep original 'title' instead of 'name'
    description: str | None = Field(default=None, max_length=255)
    category: str | None = Field(default=None, max_length=100)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: UUID = Field(foreign_key="user.id")
    owner: User = Relationship(back_populates="items")
    event_items: list["PackingItem"] = Relationship(back_populates="item")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: UUID
    owner_id: UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


# Packing item models
class PackingItemBase(SQLModel):
    quantity: int = Field(default=1)
    required: bool = Field(default=True)
    notes: str | None = Field(default=None, max_length=255)


class PackingItemInCreate(SQLModel):
    item_id: UUID
    quantity: int = Field(default=1)
    required: bool = Field(default=True)
    notes: str | None = None


class PackingItemCreate(SQLModel):
    item_id: UUID
    quantity: int = Field(default=1)
    required: bool = Field(default=True)
    notes: str | None = Field(default=None, max_length=255)


class PackingItemUpdate(SQLModel):
    quantity: int | None = None
    required: bool | None = None
    notes: str | None = None


class PackingItemPublic(SQLModel):
    item: ItemPublic
    quantity: int
    required: bool
    notes: str | None


# Meal-related models
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


# Event Meal Option models
class EventMealOptionCreate(SQLModel):
    meal_id: UUID
    meal_type: MealType
    day: int
    max_quantity: int | None = None


# Event-related models
class EventBase(SQLModel):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    start_date: str = Field(max_length=10)  # Format: YYYY-MM-DD
    end_date: str = Field(max_length=10)


class EventCreate(EventBase):
    packing_items: list[PackingItemInCreate] | None = None
    meal_options: list[EventMealOptionCreate] | None = None


class EventUpdate(SQLModel):
    name: str | None = Field(default=None)
    description: str | None = Field(default=None)
    start_date: str | None = Field(default=None)
    end_date: str | None = Field(default=None)
    packing_items: list[PackingItemInCreate] | None = None


class EventPublic(EventBase):
    id: UUID
    created_by_id: UUID
    packing_items: list[PackingItemPublic]


class EventsPublic(SQLModel):
    data: list[EventPublic]
    count: int


# Database models (tables)
class Event(EventBase, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_by_id: UUID = Field(foreign_key="user.id", nullable=False)
    created_by: User = Relationship(back_populates="created_events")
    attendees: list["Attendance"] = Relationship(
        back_populates="event", cascade_delete=True
    )
    packing_items: list["PackingItem"] = Relationship(
        back_populates="event", cascade_delete=True
    )
    meal_options: list["EventMealOption"] = Relationship(
        back_populates="event", cascade_delete=True
    )


class Meal(MealBase, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_by_id: UUID = Field(foreign_key="user.id")
    event_meal_options: list["EventMealOption"] = Relationship(back_populates="meal")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class EventMealOption(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    event_id: UUID = Field(foreign_key="event.id")
    meal_id: UUID = Field(foreign_key="meal.id")
    meal_type: MealType
    day: int
    max_quantity: int | None = None

    event: Event = Relationship(back_populates="meal_options")
    meal: Meal = Relationship(back_populates="event_meal_options")
    meal_choices: list["MealChoice"] = Relationship(back_populates="event_meal_option")


class PackingItem(PackingItemBase, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    event_id: UUID = Field(foreign_key="event.id")
    item_id: UUID = Field(foreign_key="item.id")
    event: Event = Relationship(back_populates="packing_items")
    item: Item = Relationship(back_populates="event_items")


class MealChoice(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    attendance_id: UUID = Field(foreign_key="attendance.id")
    event_meal_option_id: UUID = Field(foreign_key="eventmealoption.id")
    quantity: int = 1
    notes: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

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


class PackingItemsPublic(SQLModel):
    data: list[PackingItemPublic]
    count: int


class EventPackingList(SQLModel):
    """Model for event with its packing list"""

    event_id: UUID
    event_name: str
    items: PackingItemsPublic


class MealChoiceCreate(SQLModel):
    attendance_id: UUID
    event_meal_option_id: UUID
    quantity: int = 1
    notes: str | None = None


class MealChoiceUpdate(SQLModel):
    event_meal_option_id: UUID | None = None
    quantity: int | None = None
    notes: str | None = None
