import uuid
from typing import Any

from sqlalchemy import func
from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    Attendance,
    Event,
    EventCreate,
    EventUpdate,
    Item,
    ItemCreate,
    PackingItem,
    PackingItemCreate,
    User,
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


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


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


def create_packing_item(
    *,
    session: Session,
    event_id: uuid.UUID,
    item_id: uuid.UUID,
    packing_item_in: PackingItemCreate,
) -> PackingItem:
    db_packing_item = PackingItem(
        **packing_item_in.model_dump(), event_id=event_id, item_id=item_id
    )
    session.add(db_packing_item)
    session.commit()
    session.refresh(db_packing_item)
    return db_packing_item


def get_event_packing_items(
    *, session: Session, event_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> tuple[list[PackingItem], int]:
    statement = (
        select(PackingItem)
        .where(PackingItem.event_id == event_id)
        .offset(skip)
        .limit(limit)
    )
    items = session.exec(statement).all()
    count = session.exec(
        select(func.count())
        .select_from(PackingItem)
        .where(PackingItem.event_id == event_id)
    ).one()
    return items, count


def get_event_attendees(
    *, session: Session, event_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> tuple[list[Attendance], int]:
    statement = (
        select(Attendance)
        .where(Attendance.event_id == event_id)
        .offset(skip)
        .limit(limit)
    )
    attendees = session.exec(statement).all()
    count = session.exec(
        select(func.count())
        .select_from(Attendance)
        .where(Attendance.event_id == event_id)
    ).one()
    return attendees, count
