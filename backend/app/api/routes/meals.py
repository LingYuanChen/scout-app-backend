from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import Meal, MealCreate, MealPublic, MealUpdate

router = APIRouter(prefix="/meals", tags=["meals"])


@router.post("/", response_model=MealPublic)
def create_meal(
    *, session: SessionDep, current_user: CurrentUser, meal_in: MealCreate
) -> Any:
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
    if not current_user.is_superuser and current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can create meals")

    meal = Meal(**meal_in.model_dump(), created_by_id=current_user.id)
    session.add(meal)
    session.commit()
    session.refresh(meal)
    return meal


@router.get("/", response_model=list[MealPublic])
def read_meals(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """Retrieve meals."""
    if current_user.role != "superuser" and current_user.role != "teacher":
        raise HTTPException(
            status_code=403, detail="You are not authorized to view meals"
        )
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


@router.put("/{id}", response_model=MealPublic)
def update_meal(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: UUID,
    meal_in: MealUpdate,
) -> Any:
    """Update a meal."""
    meal = session.get(Meal, id)
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    if current_user.role != "superuser" and current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_data = meal_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(meal, field, value)

    session.add(meal)
    session.commit()
    session.refresh(meal)
    return meal


@router.delete("/{id}")
def delete_meal(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: UUID,
) -> Any:
    """Delete a meal."""
    meal = session.get(Meal, id)
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    if current_user.role != "superuser" and current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    session.delete(meal)
    session.commit()
    return {"message": "Meal deleted"}
