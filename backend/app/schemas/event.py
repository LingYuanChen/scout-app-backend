from uuid import UUID

from sqlmodel import Field, SQLModel

from .event_meal_option import EventMealOptionCreate, EventMealOptionPublic
from .packing import PackingEquipmentCreate, PackingEquipmentPublic


class EventBase(SQLModel):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    start_date: str = Field(max_length=10)  # Format: YYYY-MM-DD
    end_date: str = Field(max_length=10)
    coordinator_id: UUID | None = Field(foreign_key="user.id")


class EventCreate(EventBase):
    packing_equipments: list[PackingEquipmentCreate] | None = None
    meal_options: list[EventMealOptionCreate] | None = None


class EventUpdate(SQLModel):
    name: str | None = Field(default=None)
    description: str | None = Field(default=None)
    start_date: str | None = Field(default=None)
    end_date: str | None = Field(default=None)
    coordinator_id: UUID | None = Field(foreign_key="user.id")
    packing_equipments: list[PackingEquipmentCreate] | None = None
    meal_options: list[EventMealOptionCreate] | None = None


class EventPublic(EventBase):
    id: UUID
    packing_equipments: list[PackingEquipmentPublic]
    meal_options: list[EventMealOptionPublic]


class EventsPublic(SQLModel):
    data: list[EventPublic]
    count: int


class PackingEquipmentsPublic(SQLModel):
    data: list[PackingEquipmentPublic]
    count: int


class EventPackingList(SQLModel):
    event_id: UUID
    event_name: str
    equipments: PackingEquipmentsPublic
