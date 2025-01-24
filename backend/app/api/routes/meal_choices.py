from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.db import (
    Attendance,
    EventMealOption,
    MealChoice,
)
from app.schemas import (
    MealChoiceCreate,
    MealChoiceUpdate,
)

router = APIRouter(prefix="/meal-choices", tags=["meal-choices"])


@router.post("/", response_model=MealChoice)
def create_meal_choice(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    meal_choice_in: MealChoiceCreate,
) -> Any:
    """Create meal choice for an attendance."""
    # Verify attendance exists and belongs to user
    attendance = session.get(Attendance, meal_choice_in.attendance_id)
    if not attendance or attendance.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Attendance not found")

    # Verify meal option exists
    meal_option = session.get(EventMealOption, meal_choice_in.event_meal_option_id)
    if not meal_option or meal_option.event_id != attendance.event_id:
        raise HTTPException(status_code=404, detail="Meal option not found")

    meal_choice = MealChoice(
        attendance_id=meal_choice_in.attendance_id,
        event_meal_option_id=meal_choice_in.event_meal_option_id,
        quantity=meal_choice_in.quantity,
        notes=meal_choice_in.notes,
    )
    session.add(meal_choice)
    session.commit()
    session.refresh(meal_choice)
    return meal_choice


@router.get("/", response_model=list[MealChoice])
def read_meal_choices(
    session: SessionDep,
    current_user: CurrentUser,
    attendance_id: UUID | None = None,
) -> Any:
    """Get meal choices. Can filter by attendance_id."""
    statement = select(MealChoice)
    if attendance_id:
        # Verify attendance belongs to user
        attendance = session.get(Attendance, attendance_id)
        if not attendance or attendance.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Attendance not found")
        statement = statement.where(MealChoice.attendance_id == attendance_id)

    meal_choices = session.exec(statement).all()
    return meal_choices


@router.put("/{id}", response_model=MealChoice)
def update_meal_choice(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: UUID,
    meal_choice_in: MealChoiceUpdate,
) -> Any:
    """Update a meal choice."""
    meal_choice = session.get(MealChoice, id)
    if not meal_choice:
        raise HTTPException(status_code=404, detail="Meal choice not found")

    # Verify ownership
    attendance = session.get(Attendance, meal_choice.attendance_id)
    if not attendance or attendance.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # TODO: Verify meal option exists
    if meal_choice_in.event_meal_option_id is not None:
        meal_choice.event_meal_option_id = meal_choice_in.event_meal_option_id
    if meal_choice_in.quantity is not None:
        meal_choice.quantity = meal_choice_in.quantity
    if meal_choice_in.notes is not None:
        meal_choice.notes = meal_choice_in.notes

    session.add(meal_choice)
    session.commit()
    session.refresh(meal_choice)
    return meal_choice


@router.delete("/{id}")
def delete_meal_choice(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: UUID,
) -> Any:
    """Delete a meal choice."""
    meal_choice = session.get(MealChoice, id)
    if not meal_choice:
        raise HTTPException(status_code=404, detail="Meal choice not found")

    # Verify ownership
    attendance = session.get(Attendance, meal_choice.attendance_id)
    if not attendance or attendance.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    session.delete(meal_choice)
    session.commit()
    return {"message": "Meal choice deleted"}
