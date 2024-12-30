import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Event,
    EventCreate,
    EventPublic,
    EventsPublic,
    EventUpdate,
    Item,
    PackingItem,
)

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/", response_model=EventsPublic)
def read_events(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve events.
    """
    if current_user:
        count_statement = select(func.count()).select_from(Event)
        count = session.exec(count_statement).one()
        statement = select(Event).offset(skip).limit(limit)
        events = session.exec(statement).all()
    return EventsPublic(data=events, count=count)


@router.get("/{id}", response_model=EventPublic)
def read_event(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get event by ID.
    """
    event = session.get(Event, id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if not current_user.is_superuser and (event.created_by_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return event


@router.post("/", response_model=EventPublic)
def create_event(
    *, session: SessionDep, current_user: CurrentUser, event_in: EventCreate
) -> Any:
    """
    Create new event with packing items.
    Only teachers and superusers can create events.
    """
    if not current_user.is_superuser and current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can create events")

    # Create event
    event = Event.model_validate(
        event_in.model_dump(exclude={"packing_items"}),
        update={"created_by_id": current_user.id},
    )
    session.add(event)
    session.commit()
    session.refresh(event)

    # Add packing items if provided
    if event_in.packing_items:
        for item_data in event_in.packing_items:
            # Verify item exists
            item = session.get(Item, item_data.item_id)
            if not item:
                raise HTTPException(
                    status_code=404,
                    detail=f"Item with id {item_data.item_id} not found",
                )
            # Create packing item with all details
            packing_item = PackingItem(
                event_id=event.id,
                item_id=item_data.item_id,
                quantity=item_data.quantity,
                required=item_data.required,
                notes=item_data.notes,
            )
            session.add(packing_item)
        session.commit()
        session.refresh(event)
    return event


@router.put("/{id}", response_model=EventPublic)
def update_event(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    event_in: EventUpdate,
) -> Any:
    """
    Update an event and its packing items.
    """
    # Check event exists and permissions
    event = session.get(Event, id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if not current_user.is_superuser and (event.created_by_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    # Update event basic info
    update_dict = event_in.model_dump(exclude_unset=True, exclude={"packing_items"})
    event.sqlmodel_update(update_dict)
    session.add(event)

    # Update packing items if provided
    if event_in.packing_items is not None:
        # First verify all items exist
        for item_data in event_in.packing_items:
            if not session.get(Item, item_data.item_id):
                raise HTTPException(
                    status_code=404,
                    detail=f"Item with id {item_data.item_id} not found",
                )

        session.query(PackingItem).filter(PackingItem.event_id == event.id).delete()  # type: ignore[arg-type]

        # Add new packing items
        for item_data in event_in.packing_items:
            packing_item = PackingItem(
                event_id=event.id,
                item_id=item_data.item_id,
                quantity=item_data.quantity,
                required=item_data.required,
                notes=item_data.notes,
            )
            session.add(packing_item)

    session.commit()
    session.refresh(event)
    return event


@router.delete("/{id}")
def delete_event(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
) -> Any:
    """
    Delete an event.
    """
    event = session.get(Event, id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if not current_user.is_superuser and (event.created_by_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    # No need to manually delete packing items
    # They will be automatically deleted due to cascade_delete=True
    session.delete(event)
    session.commit()
    return {"message": "Event deleted"}
