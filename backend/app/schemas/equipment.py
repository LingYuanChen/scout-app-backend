from uuid import UUID

from sqlmodel import Field, SQLModel


class EquipmentBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    category: str | None = Field(default=None, max_length=100)


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(EquipmentBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


class EquipmentPublic(EquipmentBase):
    id: UUID
    owner_id: UUID


class EquipmentsPublic(SQLModel):
    data: list[EquipmentPublic]
    count: int
