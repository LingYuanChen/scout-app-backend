import uuid

from sqlmodel import Session, select

from app.models import Event, Item, PackingItem
from app.tests.utils.item import create_random_item
from app.tests.utils.user import (
    create_random_teacher,
)
from app.tests.utils.utils import random_lower_string


def create_random_event(
    db: Session, *, created_by_id: uuid.UUID | None = None, packing_items_count: int = 0
) -> Event:
    """Create a random event with optional packing items.

    Args:
        db: Database session
        created_by_id: Optional ID of the creator (teacher)
        packing_items_count: Number of packing items to create/attach
            If > 0, will try to use existing items first, then create new ones if needed
    """
    if created_by_id is None:
        user = create_random_teacher(db)
        created_by_id = user.id

    event = Event(
        name=random_lower_string(),
        description=random_lower_string(),
        start_date="2024-07-01",
        end_date="2024-07-05",
        created_by_id=created_by_id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    # Add packing items if requested
    if packing_items_count > 0:
        # First try to get existing items
        existing_items = list(db.exec(select(Item).limit(packing_items_count)).all())

        # Calculate how many new items we need to create
        items_needed = packing_items_count - len(existing_items)

        # Create new items if necessary
        if items_needed > 0:
            for _ in range(items_needed):
                existing_items.append(create_random_item(db))

        # Create packing items for the event
        for item in existing_items[:packing_items_count]:
            packing_item = PackingItem(
                event_id=event.id,
                item_id=item.id,
                quantity=2,  # Default quantity
                required=True,  # Default required status
                notes=f"Test note for {item.title}",
            )
            db.add(packing_item)

        db.commit()
        db.refresh(event)

    return event
