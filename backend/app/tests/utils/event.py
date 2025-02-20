import uuid

from sqlmodel import Session, select

from app.db import Equipment, Event, PackingEquipment
from app.tests.utils.equipment import create_random_equipment
from app.tests.utils.user import create_random_staff
from app.tests.utils.utils import random_lower_string


def create_random_event(
    db: Session,
    *,
    coordinator_id: uuid.UUID | None = None,
    packing_equipment_count: int = 0,
) -> Event:
    """Create a random event with optional packing items.

    Args:
        db: Database session
        coordinator_id: Event coordinator
        packing_items_count: Number of packing items to create/attach
            If > 0, will try to use existing items first, then create new ones if needed
    """
    if coordinator_id is None:
        user = create_random_staff(db)
        coordinator_id = user.id

    event = Event(
        name=random_lower_string(),
        description=random_lower_string(),
        start_date="2024-07-01",
        end_date="2024-07-05",
        coordinator_id=coordinator_id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    # Add packing items if requested
    if packing_equipment_count > 0:
        # First try to get existing items
        existing_items = list(
            db.exec(select(Equipment).limit(packing_equipment_count)).all()
        )

        # Calculate how many new items we need to create
        items_needed = packing_equipment_count - len(existing_items)

        # Create new items if necessary
        if items_needed > 0:
            for _ in range(items_needed):
                existing_items.append(create_random_equipment(db))

        # Create packing items for the event
        for equipment in existing_items[:packing_equipment_count]:
            packing_equipment = PackingEquipment(
                event_id=event.id,
                equipment_id=equipment.id,
                quantity=2,  # Default quantity
                required=True,  # Default required status
                notes=f"Test note for {equipment.title}",
            )
            db.add(packing_equipment)

        db.commit()
        db.refresh(event)

    return event
