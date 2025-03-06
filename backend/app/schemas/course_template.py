from uuid import UUID
from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, SQLModel

from .equipment import EquipmentPublic


class CourseTemplateBase(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    time_required: float = Field(default=0.0)
    location: str = Field(max_length=255)


class CourseTemplateCreate(CourseTemplateBase):
    created_by: UUID
    equipments: List[UUID] = []  


class CourseTemplateUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    time_required: Optional[float] = None
    location: Optional[str] = Field(default=None, max_length=255)
    equipments: Optional[List[UUID]] = None  


class CourseTemplatePublic(CourseTemplateBase):
    id: UUID
    created_by: UUID
    created_at: datetime
    equipments: List[EquipmentPublic] = []  
