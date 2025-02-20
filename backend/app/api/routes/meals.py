from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from app.api.deps import (
    MealDataDep,
    SessionDep,
    get_current_staff,
    get_current_teacher,
)
from app.db import Meal
from app.schemas import (
    MealPublic,
)

router = APIRouter(prefix="/meals", tags=["meals"])


@router.post(
    "/",
    dependencies=[Depends(get_current_teacher)],
    response_model=MealPublic,
)
def create_meal(*, session: SessionDep, meal_in: MealDataDep) -> Any:
    """
    Create new meal. Only teachers and superusers can create meals.

    Example request body:    ```json
    {
        "name": "Spaghetti Bolognese",
        "description": "Classic Italian pasta with meat sauce",
        "price": 15.00,
        "is_vegetarian": false,
        "is_beef": true,
        "calories": 650
    }    ```
    """
    meal = Meal(**meal_in.model_dump())
    session.add(meal)
    session.commit()
    session.refresh(meal)
    return meal


@router.get(
    "/",
    dependencies=[Depends(get_current_staff)],
    response_model=list[MealPublic],
)
def read_meals(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """Retrieve meals."""

    statement = select(Meal).offset(skip).limit(limit)
    meals = session.exec(statement).all()
    return meals


@router.get("/{id}", response_model=MealPublic)
def read_meal(session: SessionDep, id: UUID) -> Any:
    """Get meal by ID."""
    meal = session.get(Meal, id)
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    return meal


@router.put(
    "/{id}",
    dependencies=[Depends(get_current_teacher)],
    response_model=MealPublic,
)
def update_meal(
    *,
    session: SessionDep,
    id: UUID,
    meal_in: MealDataDep,
) -> Any:
    """Update a meal."""
    meal = session.get(Meal, id)
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    update_data = meal_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(meal, field, value)

    session.add(meal)
    session.commit()
    session.refresh(meal)
    return meal


@router.delete(
    "/{id}",
    dependencies=[Depends(get_current_teacher)],
)
def delete_meal(
    *,
    session: SessionDep,
    id: UUID,
) -> Any:
    """Delete a meal."""
    meal = session.get(Meal, id)
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    session.delete(meal)
    session.commit()
    return {"message": "Meal deleted"}
