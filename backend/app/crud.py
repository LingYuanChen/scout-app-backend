import uuid
from typing import Any

from sqlalchemy import func
from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.db import (
    Attendance,
    Equipment,
    Event,
    PackingEquipment,
    User,
)
from app.schemas import (
    EquipmentCreate,
    EventCreate,
    EventUpdate,
    PackingEquipmentCreate,
    UserCreate,
    UserUpdate,
)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_equipment(*, session: Session, equipment_in: EquipmentCreate) -> Equipment:
    db_equipment = Equipment.model_validate(equipment_in)
    session.add(db_equipment)
    session.commit()
    session.refresh(db_equipment)
    return db_equipment


def create_event(
    *, session: Session, event_in: EventCreate, created_by_id: uuid.UUID
) -> Event:
    db_event = Event.model_validate(event_in, update={"created_by_id": created_by_id})
    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event


def update_event(*, session: Session, db_event: Event, event_in: EventUpdate) -> Event:
    """
    Update event.
    """
    event_data = event_in.model_dump(exclude_unset=True)
    db_event.sqlmodel_update(event_data)
    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event


def delete_event(*, session: Session, event: Event) -> None:
    """
    Delete event.
    """
    session.delete(event)
    session.commit()


def create_packing_equipment(
    *,
    session: Session,
    event_id: uuid.UUID,
    equipment_id: uuid.UUID,
    packing_equipment_in: PackingEquipmentCreate,
) -> PackingEquipment:
    db_packing_equipment = PackingEquipment(
        **packing_equipment_in.model_dump(),
        event_id=event_id,
        equipment_id=equipment_id,
    )
    session.add(db_packing_equipment)
    session.commit()
    session.refresh(db_packing_equipment)
    return db_packing_equipment


def get_event_packing_equipments(
    *, session: Session, event_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> tuple[list[PackingEquipment], int]:
    statement = (
        select(PackingEquipment)
        .where(PackingEquipment.event_id == event_id)
        .offset(skip)
        .limit(limit)
    )
    equipments = list(session.exec(statement).all())
    count = session.exec(
        select(func.count())
        .select_from(PackingEquipment)
        .where(PackingEquipment.event_id == event_id)
    ).one()
    return equipments, count


def get_event_attendees(
    *, session: Session, event_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> tuple[list[Attendance], int]:
    statement = (
        select(Attendance)
        .where(Attendance.event_id == event_id)
        .offset(skip)
        .limit(limit)
    )
    attendees = list(session.exec(statement).all())
    count = session.exec(
        select(func.count())
        .select_from(Attendance)
        .where(Attendance.event_id == event_id)
    ).one()
    return attendees, count
