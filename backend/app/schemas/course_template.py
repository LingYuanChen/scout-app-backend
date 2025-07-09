from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel

from .equipment import EquipmentPublic


class CourseTemplateBase(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    time_required: float = Field(default=0.0)
    location: str = Field(max_length=255)


class CourseTemplateCreate(CourseTemplateBase):
    # created_by: UUID
    equipments: list[UUID] = Field(default_factory=list)


class CourseTemplateUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    time_required: float | None = None
    location: str | None = Field(default=None, max_length=255)
    equipments: list[UUID] | None = None


class CourseTemplatePublic(CourseTemplateBase):
    id: UUID
    created_by: UUID
    created_at: datetime
    equipments: list[EquipmentPublic] = Field(default_factory=list)
