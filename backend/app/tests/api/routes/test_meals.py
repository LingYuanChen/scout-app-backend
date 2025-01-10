import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils.meal import create_random_meal  # We'll create this utility


def test_create_meal(client: TestClient, teacher_token_headers: dict[str, str]) -> None:
    data = {
        "name": "Test Meal",
        "description": "Test Description",
        "price": 15.50,
        "is_vegetarian": False,
        "is_beef": True,
        "calories": 650,
    }
    response = client.post(
        f"{settings.API_V1_STR}/meals/",
        headers=teacher_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["description"] == data["description"]
    assert content["price"] == data["price"]
    assert "id" in content
    assert "created_by_id" in content


def test_create_meal_by_normal_user(
    client: TestClient, student_token_headers: dict[str, str]
) -> None:
    data = {
        "name": "Test Meal",
        "description": "Test Description",
        "price": 15.50,
        "is_vegetarian": False,
        "is_beef": True,
        "calories": 650,
    }
    response = client.post(
        f"{settings.API_V1_STR}/meals/",
        headers=student_token_headers,
        json=data,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Only teachers can create meals"


def test_read_meal(
    client: TestClient, teacher_token_headers: dict[str, str], db: Session
) -> None:
    meal = create_random_meal(db)
    response = client.get(
        f"{settings.API_V1_STR}/meals/{meal.id}",
        headers=teacher_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == meal.name
    assert content["description"] == meal.description
    assert content["id"] == str(meal.id)
    assert content["created_by_id"] == str(meal.created_by_id)


def test_read_meal_not_found(
    client: TestClient, teacher_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/meals/{uuid.uuid4()}",
        headers=teacher_token_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Meal not found"


def test_read_meals(
    client: TestClient, teacher_token_headers: dict[str, str], db: Session
) -> None:
    create_random_meal(db)
    create_random_meal(db)
    response = client.get(
        f"{settings.API_V1_STR}/meals/",
        headers=teacher_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content) >= 2


def test_update_meal(
    client: TestClient, teacher_token_headers: dict[str, str], db: Session
) -> None:
    meal = create_random_meal(db)
    data = {
        "name": "Updated Meal",
        "description": "Updated Description",
        "price": 20.50,
    }
    response = client.put(
        f"{settings.API_V1_STR}/meals/{meal.id}",
        headers=teacher_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["description"] == data["description"]
    assert content["price"] == data["price"]
    assert content["id"] == str(meal.id)


def test_update_meal_not_found(
    client: TestClient, teacher_token_headers: dict[str, str]
) -> None:
    data = {"name": "Updated Meal"}
    response = client.put(
        f"{settings.API_V1_STR}/meals/{uuid.uuid4()}",
        headers=teacher_token_headers,
        json=data,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Meal not found"


def test_delete_meal(
    client: TestClient, teacher_token_headers: dict[str, str], db: Session
) -> None:
    meal = create_random_meal(db)
    response = client.delete(
        f"{settings.API_V1_STR}/meals/{meal.id}",
        headers=teacher_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Meal deleted"


def test_delete_meal_not_found(
    client: TestClient, teacher_token_headers: dict[str, str]
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}/meals/{uuid.uuid4()}",
        headers=teacher_token_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Meal not found"
