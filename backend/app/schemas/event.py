from uuid import UUID

from sqlmodel import Field, SQLModel

from .event_meal_option import EventMealOptionCreate
from .packing import PackingItemCreate, PackingItemPublic


class EventBase(SQLModel):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    start_date: str = Field(max_length=10)  # Format: YYYY-MM-DD
    end_date: str = Field(max_length=10)


class EventCreate(EventBase):
    packing_items: list[PackingItemCreate] | None = None
    meal_options: list[EventMealOptionCreate] | None = None


class EventUpdate(SQLModel):
    name: str | None = Field(default=None)
    description: str | None = Field(default=None)
    start_date: str | None = Field(default=None)
    end_date: str | None = Field(default=None)
    packing_items: list[PackingItemCreate] | None = None


class EventPublic(EventBase):
    id: UUID
    created_by_id: UUID
    packing_items: list[PackingItemPublic]


class EventsPublic(SQLModel):
    data: list[EventPublic]
    count: int


class PackingItemsPublic(SQLModel):
    data: list[PackingItemPublic]
    count: int


class EventPackingList(SQLModel):
    event_id: UUID
    event_name: str
    items: PackingItemsPublic
