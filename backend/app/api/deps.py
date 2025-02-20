from collections.abc import Generator
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, Path, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session, select

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.db import Attendance, Event, User
from app.db.enums import RoleType
from app.schemas import TokenPayload
from app.schemas.event import EventCreate, EventUpdate
from app.schemas.meal import MealCreate, MealUpdate

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_student(current_user: CurrentUser) -> User:
    """Base level - any authenticated user can access"""
    return current_user


CurrentStudent = Annotated[User, Depends(get_current_student)]


def get_current_staff(current_user: CurrentUser) -> User:
    """Staff level - verifies user is staff or above"""
    if current_user.role_type not in {RoleType.STAFF, RoleType.TEACHER, RoleType.ADMIN}:
        raise HTTPException(
            status_code=403,
            detail="Only staff members and above can access this resource",
        )
    return current_user


CurrentStaff = Annotated[User, Depends(get_current_staff)]


def get_current_teacher(current_user: CurrentUser) -> User:
    """Teacher level - verifies user is teacher or admin"""
    if current_user.role_type not in {RoleType.TEACHER, RoleType.ADMIN}:
        raise HTTPException(
            status_code=403, detail="Only teachers and admins can access this resource"
        )
    return current_user


CurrentTeacher = Annotated[User, Depends(get_current_teacher)]


def get_current_admin(current_user: CurrentUser) -> User:
    """Admin level - verifies user is admin only"""
    if current_user.role_type != RoleType.ADMIN:
        raise HTTPException(
            status_code=403, detail="Only admins can access this resource"
        )
    return current_user


CurrentAdmin = Annotated[User, Depends(get_current_admin)]


def get_event(event_id: UUID = Path(...), session: Session = Depends(get_db)) -> Event:
    """Get event by ID"""
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


def get_attendance(
    event_id: UUID = Path(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> Attendance | None:
    """Get attendance for current user and event"""
    statement = select(Attendance).where(
        Attendance.user_id == current_user.id, Attendance.event_id == event_id
    )
    return session.exec(statement).first()


EventDep = Annotated[Event, Depends(get_event)]
AttendanceDep = Annotated[Attendance | None, Depends(get_attendance)]


def get_user_attendances(
    current_user: CurrentUser = Depends(get_current_user),
    session: SessionDep = Depends(get_db),
) -> list[Attendance]:
    """Get all events a user is attending"""
    statement = select(Attendance).where(
        Attendance.user_id == current_user.id, Attendance.is_attending is True
    )
    return list(session.exec(statement).all())


UserAttendancesDep = Annotated[list[Attendance], Depends(get_user_attendances)]


def validate_meal_data(meal: MealCreate | MealUpdate) -> MealCreate | MealUpdate:
    if meal.calories is not None and meal.calories < 0:
        raise HTTPException(status_code=400, detail="Calories cannot be negative")
    if meal.price is not None and meal.price < 0:
        raise HTTPException(status_code=400, detail="Price cannot be negative")
    return meal


MealDataDep = Annotated[MealCreate | MealUpdate, Depends(validate_meal_data)]


def get_event_coordinator_or_above(event: EventDep, current_user: CurrentUser) -> Event:
    """
    Verify user is the event coordinator or has a higher role (admin).
    """
    if current_user.role_type == RoleType.ADMIN:
        return event

    if event.coordinator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this event",
        )
    return event


def validate_event_data(
    event_data: EventCreate | EventUpdate, session: SessionDep
) -> EventCreate | EventUpdate:
    """
    Validate event data for constraints like coordinator existence.
    """
    # Check for non-existent coordinator
    if event_data.coordinator_id:
        coordinator = session.get(User, event_data.coordinator_id)
        if not coordinator:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {event_data.coordinator_id} not found",
            )
    return event_data


EventDataDep = Annotated[EventCreate | EventUpdate, Depends(validate_event_data)]
