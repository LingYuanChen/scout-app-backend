import uuid

from sqlmodel import Session, delete

from app.db import Attendance, Event, PackingItem
from app.tests.utils.event import create_random_event
from app.tests.utils.item import create_random_item
from app.tests.utils.user import create_random_user


def create_random_attendance(
    db: Session, *, user_id: uuid.UUID | None = None, event_id: uuid.UUID | None = None
) -> Attendance:
    if user_id is None:
        user = create_random_user(db)
        user_id = user.id

    if event_id is None:
        event = create_random_event(db)
        event_id = event.id

    attendance = Attendance(user_id=user_id, event_id=event_id, is_attending=True)
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


def create_attendance_with_packing_items(
    db: Session,
    *,
    user_id: uuid.UUID | None = None,
    num_items: int = 1,
) -> Attendance:
    """Create attendance with packing items for testing"""
    # 1. Creates attendance record in attendance table
    attendance = create_random_attendance(db, user_id=user_id)

    # 2. For each item:
    for _ in range(num_items):
        # Creates item record in item table
        item = create_random_item(db)

        # Creates packing_item record in packing_item table
        # This links to both event and item via foreign keys
        packing_item = PackingItem(
            event_id=attendance.event_id,  # Foreign key to event
            item_id=item.id,  # Foreign key to item
            quantity=2,
            required=True,
        )
        # Adds to packing_item table
        db.add(packing_item)

    # 3. Commits all changes to database
    db.commit()
    return attendance


def clean_attendance_tables(db: Session) -> None:
    """Clean up all attendance-related tables in correct order"""
    try:
        # Delete in correct order (children first)
        tables = [
            PackingItem,  # Delete first (references Attendance)
            Attendance,  # Delete second (references Event)
            Event,  # Delete last
        ]

        for table in tables:
            statement = delete(table)
            db.execute(statement)
        db.commit()
    except Exception as e:
        print(f"Error cleaning attendance tables: {e}")
        db.rollback()
