from sqlmodel import Session

from app import crud
from app.db import Equipment
from app.schemas import EquipmentCreate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_equipment(db: Session) -> Equipment:
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    title = random_lower_string()
    description = random_lower_string()
    equipment_in = EquipmentCreate(title=title, description=description)
    return crud.create_equipment(
        session=db, equipment_in=equipment_in, owner_id=owner_id
    )
