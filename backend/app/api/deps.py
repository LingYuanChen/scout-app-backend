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
from app.schemas import TokenPayload

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


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


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
