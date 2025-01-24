import uuid

from sqlmodel import Session, delete

from app.db import (
    Attendance,
    Event,
    EventMealOption,
    Meal,
    MealChoice,
    MealType,
)
from app.tests.utils.user import (
    create_random_teacher,
)
from app.tests.utils.utils import random_lower_string


def create_random_meal(db: Session, *, created_by_id: uuid.UUID | None = None) -> Meal:
    if created_by_id is None:
        user = create_random_teacher(db)
        created_by_id = user.id

    meal = Meal(
        name=random_lower_string(),
        description=random_lower_string(),
        price=15.50,
        is_vegetarian=False,
        is_beef=True,
        calories=650,
        created_by_id=created_by_id,
    )
    db.add(meal)
    db.commit()
    db.refresh(meal)
    return meal


def create_meal_option(
    db: Session, event_id: uuid.UUID, meal_id: uuid.UUID
) -> EventMealOption:
    meal_option = EventMealOption(
        event_id=event_id,
        meal_id=meal_id,
        meal_type=MealType.LUNCH,
        day=1,
        max_quantity=50,
    )
    db.add(meal_option)
    db.commit()
    db.refresh(meal_option)
    return meal_option


def create_random_meal_choice(
    db: Session,
    *,
    attendance_id: uuid.UUID,
    event_meal_option_id: uuid.UUID,
    quantity: int = 1,
    notes: str | None = None,
) -> MealChoice:
    meal_choice = MealChoice(
        attendance_id=attendance_id,
        event_meal_option_id=event_meal_option_id,
        quantity=quantity,
        notes=notes,
    )
    db.add(meal_choice)
    db.commit()
    db.refresh(meal_choice)
    return meal_choice


def clean_meal_tables(db: Session) -> None:
    """Clean up all meal-related tables in correct order"""
    try:
        # Delete in correct order (children first)
        tables = [
            MealChoice,  # Delete first (references Attendance)
            EventMealOption,  # Delete second (references Event)
            Meal,  # Delete last
            Attendance,
            Event,
        ]

        for table in tables:
            statement = delete(table)
            db.execute(statement)
        db.commit()
    except Exception as e:
        print(f"Error cleaning attendance tables: {e}")
        db.rollback()
