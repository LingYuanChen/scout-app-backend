from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import delete, func, select

from app.api.deps import (
    CurrentUser,
    EventDataDep,
    SessionDep,
    get_current_teacher,
)
from app.db import (
    Equipment,
    Event,
    EventMealOption,
    Meal,
    PackingEquipment,
)
from app.schemas import (
    EventPublic,
    EventsPublic,
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
def read_event(
    session: SessionDep,
    id: UUID,
) -> Any:
    """
    Get event by ID.
    """
    event = session.get(Event, id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post(
    "/",
    dependencies=[Depends(get_current_teacher)],
    response_model=EventPublic,
)
def create_event(*, session: SessionDep, event_in: EventDataDep) -> Any:
    """
    Create new event with packing Equipments and meal options.
    Only teachers and superusers can create events.
    """

    # Create event
    event = Event.model_validate(
        event_in.model_dump(exclude={"packing_equipments", "meal_options"})
    )
    session.add(event)
    session.commit()
    session.refresh(event)

    # Add packing Equipments if provided
    if event_in.packing_equipments:
        for equipment_data in event_in.packing_equipments:
            # Verify equipment exists
            equipment = session.get(Equipment, equipment_data.equipment_id)
            if not equipment:
                raise HTTPException(
                    status_code=404,
                    detail=f"equipment with id {equipment_data.equipment_id} not found",
                )
            # Create packing equipment with all details
            packing_equipment = PackingEquipment(
                event_id=event.id,
                equipment_id=equipment_data.equipment_id,
                quantity=equipment_data.quantity,
                required=equipment_data.required,
                notes=equipment_data.notes,
            )
            session.add(packing_equipment)
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


@router.put(
    "/{id}",
    dependencies=[Depends(get_current_teacher)],
    response_model=EventPublic,
)
def update_event(
    *,
    session: SessionDep,
    id: UUID,
    event_in: EventDataDep,
) -> Any:
    """
    Update an event and its packing equipments.
    """
    # Check event exists and permissions
    event = session.get(Event, id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Update event basic info
    update_dict = event_in.model_dump(
        exclude_unset=True, exclude={"packing_equipments"}
    )
    event.sqlmodel_update(update_dict)
    session.add(event)

    # Update packing equipments if provided
    if event_in.packing_equipments is not None:
        # First verify all equipments exist
        for equipment_data in event_in.packing_equipments:
            if not session.get(Equipment, equipment_data.equipment_id):
                raise HTTPException(
                    status_code=404,
                    detail=f"equipment with id {equipment_data.equipment_id} not found",
                )

        statement = delete(PackingEquipment).where(
            PackingEquipment.event_id == event.id  # type: ignore
        )
        session.exec(statement)  # type: ignore
        # Add new packing equipments
        for equipment_data in event_in.packing_equipments:
            packing_equipment = PackingEquipment(
                event_id=event.id,
                equipment_id=equipment_data.equipment_id,
                quantity=equipment_data.quantity,
                required=equipment_data.required,
                notes=equipment_data.notes,
            )
            session.add(packing_equipment)

    session.commit()
    session.refresh(event)
    return event


@router.delete(
    "/{id}",
    dependencies=[Depends(get_current_teacher)],
)
def delete_event(
    *,
    session: SessionDep,
    id: UUID,
) -> Any:
    """
    Delete an event.
    """
    event = session.get(Event, id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    session.delete(event)
    session.commit()
    return {"message": "Event deleted"}
