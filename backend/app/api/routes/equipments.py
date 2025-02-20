from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app import crud
from app.api.deps import (
    CurrentUser,
    EventDep,
    SessionDep,
    get_current_teacher,
)
from app.db import Attendance, Equipment, Event, PackingEquipment
from app.schemas import (
    EquipmentCreate,
    EquipmentPublic,
    EquipmentsPublic,
    EquipmentUpdate,
    Message,
    PackingEquipmentCreate,
    PackingEquipmentPublic,
    PackingEquipmentsPublic,
)

router = APIRouter(prefix="/equipments", tags=["equipments"])


@router.get(
    "/",
    dependencies=[Depends(get_current_teacher)],
    response_model=EquipmentsPublic,
)
def read_equipments(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve equipments catalog.
    Only teachers and superusers can access this endpoint.
    """
    count_statement = select(func.count()).select_from(Equipment)
    count = session.exec(count_statement).one()
    statement = select(Equipment).offset(skip).limit(limit)
    equipments = session.exec(statement).all()
    return EquipmentsPublic(data=equipments, count=count)


@router.get(
    "/{id}",
    dependencies=[Depends(get_current_teacher)],
    response_model=EquipmentPublic,
)
def read_equipment(session: SessionDep, id: UUID) -> Any:
    """
    Get equipment by ID.
    """
    equipment = session.get(Equipment, id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment


@router.post(
    "/",
    dependencies=[Depends(get_current_teacher)],
    response_model=EquipmentPublic,
)
def create_equipment(*, session: SessionDep, equipment_in: EquipmentCreate) -> Any:
    """
    Create new equipment in catalog.
    Only teachers and superusers can create equipments.
    """

    equipment = Equipment.model_validate(equipment_in)
    session.add(equipment)
    session.commit()
    session.refresh(equipment)
    return equipment


@router.put(
    "/{id}",
    dependencies=[Depends(get_current_teacher)],
    response_model=EquipmentPublic,
)
def update_equipment(
    *,
    session: SessionDep,
    id: UUID,
    equipment_in: EquipmentUpdate,
) -> Any:
    """
    Update an equipment.
    Only the teacher who created the equipment or superusers can update it.
    """
    equipment = session.get(Equipment, id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    update_dict = equipment_in.model_dump(exclude_unset=True)
    equipment.sqlmodel_update(update_dict)
    session.add(equipment)
    session.commit()
    session.refresh(equipment)
    return equipment


@router.delete(
    "/{id}",
    dependencies=[Depends(get_current_teacher)],
)
def delete_equipment(session: SessionDep, id: UUID) -> Message:
    """
    Delete an equipment.
    Only the teacher who created the equipment or superusers can delete it.
    """
    equipment = session.get(Equipment, id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    session.delete(equipment)
    session.commit()
    return Message(message="Equipment deleted successfully")


@router.post(
    "/{event_id}/packing",
    dependencies=[Depends(get_current_teacher)],
    response_model=PackingEquipmentPublic,
)
def add_packing_equipment(
    *,
    session: SessionDep,
    event: EventDep,
    packing_equipment_in: PackingEquipmentCreate,
) -> Any:
    """
    Add an equipment to event's packing list.
    """

    equipment = session.get(Equipment, packing_equipment_in.equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    packing_equipment = crud.create_packing_equipment(
        session=session,
        event_id=event.id,
        equipment_id=equipment.id,
        packing_equipment_in=packing_equipment_in,
    )
    return packing_equipment


@router.get("/event/{event_id}/packing", response_model=PackingEquipmentsPublic)
def list_packing_equipments(
    *,
    session: SessionDep,
    event_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    List all packing equipments for an event.
    """
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    equipments, count = crud.get_event_packing_equipments(
        session=session, event_id=event_id, skip=skip, limit=limit
    )
    return PackingEquipmentsPublic(data=equipments, count=count)


# For students to view equipments in an event they're attending
@router.get("/event/{event_id}", response_model=PackingEquipmentsPublic)
def get_event_equipments(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    event_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get all equipments required for an event.
    Students must be attending the event to see its packing list.
    """
    # Check if user is attending the event
    attendance = session.exec(
        select(Attendance).where(
            Attendance.user_id == current_user.id, Attendance.event_id == event_id
        )
    ).first()

    if not attendance:
        raise HTTPException(
            status_code=403, detail="Must be attending the event to view packing list"
        )

    # Get packing equipments for the event
    statement = (
        select(PackingEquipment)
        .where(PackingEquipment.event_id == event_id)
        .offset(skip)
        .limit(limit)
    )
    equipments = session.exec(statement).all()
    count = len(equipments)

    return PackingEquipmentsPublic(data=equipments, count=count)
