from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlmodel import delete, func, select

from app.api.deps import CurrentUser, SessionDep
from app.db import (
    Event,
    EventMealOption,
    Item,
    Meal,
    PackingItem,
    User,
)
from app.schemas import (
    EventCreate,
    EventPublic,
    EventsPublic,
    EventUpdate,
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
def read_event(session: SessionDep, current_user: CurrentUser, id: UUID) -> Any:
    """
    Get event by ID.
    """
    user = session.get(User, current_user.id)
    event = session.get(Event, id)
    if not user:
        raise HTTPException(
            status_code=403, detail="You are not authorized to view this event"
        )
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/", response_model=EventPublic)
def create_event(
    *, session: SessionDep, current_user: CurrentUser, event_in: EventCreate
) -> Any:
    """
    Create new event with packing items and meal options.
    Only teachers and superusers can create events.
    """
    if current_user.role != "superuser" and current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can create events")

    # Create event
    event = Event.model_validate(
        event_in.model_dump(exclude={"packing_items", "meal_options"}),
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

    # Add meal options if provided
    if event_in.meal_options:
        for meal_option in event_in.meal_options:
            # Verify meal exists
            meal = session.get(Meal, meal_option.meal_id)
            if not meal:
                raise HTTPException(
                    status_code=404,
                    detail=f"Meal with id {meal_option.meal_id} not found",
                )
            # Create event meal option
            event_meal = EventMealOption(event_id=event.id, **meal_option.model_dump())
            session.add(event_meal)
        session.commit()
        session.refresh(event)

    return event


@router.put("/{id}", response_model=EventPublic)
def update_event(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: UUID,
    event_in: EventUpdate,
) -> Any:
    """
    Update an event and its packing items.
    """
    # Check event exists and permissions
    event = session.get(Event, id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if current_user.role != "superuser" and current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can update events")

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

        statement = delete(PackingItem).where(PackingItem.event_id == event.id)  # type: ignore
        session.exec(statement)  # type: ignore
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
    id: UUID,
) -> Any:
    """
    Delete an event.
    """
    event = session.get(Event, id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if current_user.role != "superuser" and current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can delete events")

    # No need to manually delete packing items
    # They will be automatically deleted due to cascade_delete=True
    session.delete(event)
    session.commit()
    return {"message": "Event deleted"}
