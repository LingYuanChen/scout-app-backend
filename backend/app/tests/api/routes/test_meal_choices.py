from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils.attendance import create_random_attendance
from app.tests.utils.meal import (
    clean_meal_tables,
    create_meal_option,
    create_random_meal,
    create_random_meal_choice,
)
from app.tests.utils.utils import get_user_id_from_token


def test_create_meal_choice(
    client: TestClient, student_token_headers: dict[str, str], db: Session
) -> None:
    user_id = get_user_id_from_token(client, student_token_headers)
    attendance = create_random_attendance(db, user_id=user_id)
    meal = create_random_meal(db)
    meal_option = create_meal_option(db, attendance.event_id, meal.id)

    data = {
        "attendance_id": str(attendance.id),
        "event_meal_option_id": str(meal_option.id),
        "quantity": 2,
        "notes": "No spicy",
    }
    response = client.post(
        f"{settings.API_V1_STR}/meal-choices/",
        headers=student_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["attendance_id"] == str(attendance.id)
    assert content["event_meal_option_id"] == str(meal_option.id)
    assert content["quantity"] == 2
    assert content["notes"] == "No spicy"


def test_read_meal_choices(
    client: TestClient, student_token_headers: dict[str, str], db: Session
) -> None:
    clean_meal_tables(db)
    user_id = get_user_id_from_token(client, student_token_headers)
    attendance = create_random_attendance(db, user_id=user_id)
    meal = create_random_meal(db)
    meal_option = create_meal_option(db, attendance.event_id, meal.id)

    # Create meal choice
    create_random_meal_choice(
        db, attendance_id=attendance.id, event_meal_option_id=meal_option.id, quantity=1
    )

    response = client.get(
        f"{settings.API_V1_STR}/meal-choices/?attendance_id={attendance.id}",
        headers=student_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content) >= 1


def test_update_meal_choice(
    client: TestClient, student_token_headers: dict[str, str], db: Session
) -> None:
    clean_meal_tables(db)
    user_id = get_user_id_from_token(client, student_token_headers)
    attendance = create_random_attendance(db, user_id=user_id)
    meal = create_random_meal(db)
    meal_option = create_meal_option(db, attendance.event_id, meal.id)

    meal_choice = create_random_meal_choice(
        db, attendance_id=attendance.id, event_meal_option_id=meal_option.id, quantity=1
    )
    meal_choice_id = meal_choice.id
    # Update the meal choice
    update_data = {"quantity": 2, "notes": "Extra sauce"}
    response = client.put(
        f"{settings.API_V1_STR}/meal-choices/{meal_choice_id}",
        headers=student_token_headers,
        json=update_data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["quantity"] == 2
    assert content["notes"] == "Extra sauce"


def test_delete_meal_choice(
    client: TestClient, student_token_headers: dict[str, str], db: Session
) -> None:
    clean_meal_tables(db)
    user_id = get_user_id_from_token(client, student_token_headers)
    attendance = create_random_attendance(db, user_id=user_id)
    meal = create_random_meal(db)
    meal_option = create_meal_option(db, attendance.event_id, meal.id)

    meal_choice = create_random_meal_choice(
        db, attendance_id=attendance.id, event_meal_option_id=meal_option.id, quantity=1
    )
    meal_choice_id = meal_choice.id

    # Delete the meal choice
    response = client.delete(
        f"{settings.API_V1_STR}/meal-choices/{meal_choice_id}",
        headers=student_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Meal choice deleted"
