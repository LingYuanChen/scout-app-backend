from uuid import UUID

from sqlmodel import Field, SQLModel

from .equipment import EquipmentPublic


class PackingEquipmentBase(SQLModel):
    quantity: int = Field(default=1)
    required: bool = Field(default=True)
    notes: str | None = Field(default=None, max_length=255)


class PackingEquipmentCreate(PackingEquipmentBase):
    equipment_id: UUID


class PackingEquipmentUpdate(SQLModel):
    quantity: int | None = None
    required: bool | None = None


class PackingEquipmentPublic(PackingEquipmentBase):
    equipment: EquipmentPublic


class PackingEquipmentsPublic(SQLModel):
    data: list[PackingEquipmentPublic]
    count: int


class EventPackingList(SQLModel):
    event_id: UUID
    event_name: str
    equipments: PackingEquipmentsPublic
