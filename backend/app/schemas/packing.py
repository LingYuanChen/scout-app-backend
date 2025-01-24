from uuid import UUID

from sqlmodel import Field, SQLModel

from .item import ItemPublic


class PackingItemBase(SQLModel):
    quantity: int = Field(default=1)
    required: bool = Field(default=True)
    notes: str | None = Field(default=None, max_length=255)


class PackingItemCreate(PackingItemBase):
    item_id: UUID


class PackingItemUpdate(SQLModel):
    quantity: int | None = None
    required: bool | None = None


class PackingItemPublic(PackingItemBase):
    item: ItemPublic


class PackingItemsPublic(SQLModel):
    data: list[PackingItemPublic]
    count: int


class EventPackingList(SQLModel):
    event_id: UUID
    event_name: str
    items: PackingItemsPublic
