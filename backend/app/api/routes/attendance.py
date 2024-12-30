from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import select

import app.crud as crud
from app.api.deps import AttendanceDep, CurrentUser, EventDep, SessionDep
from app.models import Attendance, Event, Message, PackingItemsPublic

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.post("/{event_id}/join", response_model=Message)
def join_event(
    event: EventDep,
    attendance: AttendanceDep,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Student joins an event
    """
    if attendance:
        if attendance.is_attending:
            return Message(message="Already attending this event")
        attendance.is_attending = True
        session.add(attendance)
    else:
        db_attendance = Attendance(
            user_id=current_user.id, event_id=event.id, is_attending=True
        )
        session.add(db_attendance)

    session.commit()
    return Message(message="Successfully joined the event")


@router.post("/{event_id}/leave", response_model=Message)
def leave_event(
    attendance: AttendanceDep,
    session: SessionDep,
) -> Any:
    """
    Student leaves an event by removing the attendance record
    """
    if not attendance:
        return Message(message="Not attending this event")

    # Delete the attendance record instead of setting is_attending to False
    session.delete(attendance)
    session.commit()

    return Message(message="Successfully left the event")


# @router.get("/my-events", response_model=list[uuid.UUID])
@router.get("/my-events")
def get_my_events(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Get all events the student is attending
    """
    # First get the attended event IDs from Attendance table
    statement = (
        select(Attendance.event_id)
        .where(Attendance.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    event_ids = session.exec(statement).all()
    # Then get those events
    if event_ids:
        events = list(session.exec(select(Event).where(Event.id.in_(event_ids))).all())  # type: ignore[attr-defined]
        return events
    return []


@router.get("/{event_id}/packing-list", response_model=PackingItemsPublic)
def get_event_packing_list(
    *,
    session: SessionDep,
    attendance: AttendanceDep,
    event: EventDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get packing list for an event I'm attending
    """
    # Check if attending
    if not attendance:
        raise HTTPException(
            status_code=403, detail="Must be attending the event to view packing list"
        )

    items, count = crud.get_event_packing_items(
        session=session, event_id=event.id, skip=skip, limit=limit
    )
    return PackingItemsPublic(data=items, count=count)


@router.get("/my-packing-lists", response_model=list[PackingItemsPublic])
def get_my_packing_lists(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Get packing lists for all events the student is attending
    """
    # First get all events the student is attending
    attended_events_statement = (
        select(Event)
        .join(Attendance)
        .where(Attendance.user_id == current_user.id, Attendance.is_attending is True)
        .offset(skip)
        .limit(limit)
    )

    attended_events = session.exec(attended_events_statement).all()

    # Get packing lists for each event
    packing_lists = []
    for event in attended_events:
        items, count = crud.get_event_packing_items(
            session=session, event_id=event.id, skip=0, limit=100
        )
        packing_lists.append(
            PackingItemsPublic(
                data=items,
                count=count,
                event_name=event.name,  # Adding event name for reference
                event_id=event.id,  # Adding event ID for reference
            )
        )

    return packing_lists
