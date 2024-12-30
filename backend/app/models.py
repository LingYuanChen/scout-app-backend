import uuid

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


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
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    attendances: list["Attendance"] = Relationship(back_populates="user")
    created_events: list["Event"] = Relationship(back_populates="created_by")


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


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
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="user.id")
    owner: User = Relationship(back_populates="items")
    event_items: list["PackingItem"] = Relationship(back_populates="item")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


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


class EventBase(SQLModel):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    start_date: str = Field(max_length=10)  # Format: YYYY-MM-DD
    end_date: str = Field(max_length=10)


class PackingItemInCreate(SQLModel):
    item_id: uuid.UUID
    quantity: int = Field(default=1)
    required: bool = Field(default=True)
    notes: str | None = None


class EventCreate(EventBase):
    packing_items: list[PackingItemInCreate] | None = None


# Properties to receive on event update
class EventUpdate(SQLModel):
    name: str | None = Field(default=None)
    description: str | None = Field(default=None)
    start_date: str | None = Field(default=None)
    end_date: str | None = Field(default=None)
    packing_items: list[PackingItemInCreate] | None = None


# Database model
class Event(EventBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_by_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    created_by: User = Relationship(back_populates="created_events")
    attendees: list["Attendance"] = Relationship(
        back_populates="event", cascade_delete=True
    )
    meals: list["Meal"] = Relationship(back_populates="event", cascade_delete=True)
    packing_items: list["PackingItem"] = Relationship(
        back_populates="event", cascade_delete=True
    )


class PackingItemPublic(SQLModel):
    item: ItemPublic
    quantity: int
    required: bool
    notes: str | None


# Properties to return via API
class EventPublic(EventBase):
    id: uuid.UUID
    created_by_id: uuid.UUID
    packing_items: list[PackingItemPublic]


# Response model for multiple events
class EventsPublic(SQLModel):
    data: list[EventPublic]
    count: int


class Attendance(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    event_id: uuid.UUID = Field(foreign_key="event.id", nullable=False)
    is_attending: bool = Field(default=True)
    user: User = Relationship(back_populates="attendances")
    event: Event = Relationship(back_populates="attendees")
    meal_choices: list["MealChoice"] = Relationship(back_populates="attendance")


class Meal(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    event_id: uuid.UUID = Field(foreign_key="event.id", nullable=False)
    meal_time: str = Field(max_length=50)  # e.g., "Day 1 Breakfast"
    meal_option: str = Field(max_length=255)  # e.g., "Vegetarian"
    event: Event = Relationship(back_populates="meals")
    chosen_by: list["MealChoice"] = Relationship(back_populates="meal")


class MealChoice(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    attendance_id: uuid.UUID = Field(foreign_key="attendance.id", nullable=False)
    meal_id: uuid.UUID = Field(foreign_key="meal.id", nullable=False)
    quantity: int = Field(default=1)
    attendance: Attendance = Relationship(back_populates="meal_choices")
    meal: Meal = Relationship(back_populates="chosen_by")


# Properties for packing items in events
class PackingItemBase(SQLModel):
    quantity: int = Field(default=1)
    required: bool = Field(default=True)
    notes: str | None = Field(default=None, max_length=255)


class PackingItem(PackingItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    event_id: uuid.UUID = Field(foreign_key="event.id")
    item_id: uuid.UUID = Field(foreign_key="item.id")

    # Relationships
    event: "Event" = Relationship(back_populates="packing_items")
    item: Item = Relationship(back_populates="event_items")


class PackingItemCreate(SQLModel):
    item_id: uuid.UUID
    quantity: int = Field(default=1)
    required: bool = Field(default=True)
    notes: str | None = Field(default=None, max_length=255)


class PackingItemUpdate(SQLModel):
    quantity: int | None = None
    required: bool | None = None
    notes: str | None = None


class PackingItemsPublic(SQLModel):
    event_name: str
    event_id: uuid.UUID
    data: list[PackingItemPublic]
    count: int
