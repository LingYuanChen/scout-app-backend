from uuid import UUID

from sqlmodel import Field, SQLModel


class EquipmentBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    category: str = Field(min_length=1, max_length=100)
    location: str = Field(min_length=1, max_length=100)


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(EquipmentBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore
    category: str | None = Field(default=None, min_length=1, max_length=100)
    location: str | None = Field(default=None, min_length=1, max_length=100)


class EquipmentPublic(EquipmentBase):
    id: UUID


class EquipmentsPublic(SQLModel):
    data: list[EquipmentPublic]
    count: int
