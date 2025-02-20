from sqlmodel import Session

from app import crud
from app.db import Equipment
from app.schemas import EquipmentCreate
from app.tests.utils.utils import random_lower_string


def create_random_equipment(db: Session) -> Equipment:
    title = random_lower_string()
    description = random_lower_string()
    category = random_lower_string()
    location = random_lower_string()
    equipment_in = EquipmentCreate(
        title=title, description=description, category=category, location=location
    )
    return crud.create_equipment(session=db, equipment_in=equipment_in)
