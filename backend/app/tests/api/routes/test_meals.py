import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils.meal import create_random_meal


def test_create_meal(client: TestClient, teacher_token_headers: dict[str, str]) -> None:
    data = {
        "name": "Test Meal",
        "restaurant": "Test Restaurant",
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
    assert content["restaurant"] == data["restaurant"]
    assert content["description"] == data["description"]
    assert content["price"] == data["price"]
    assert content["is_vegetarian"] == data["is_vegetarian"]
    assert content["is_beef"] == data["is_beef"]
    assert content["calories"] == data["calories"]
    assert "id" in content


def test_create_meal_by_normal_user(
    client: TestClient, student_token_headers: dict[str, str]
) -> None:
    data = {
        "name": "Test Meal",
        "restaurant": "Test Restaurant",
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
    print(response.json())
    assert response.status_code == 403
    assert (
        response.json()["detail"] == "Only teachers and admins can access this resource"
    )


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
    assert content["restaurant"] == meal.restaurant
    assert content["price"] == meal.price
    assert content["is_vegetarian"] == meal.is_vegetarian
    assert content["is_beef"] == meal.is_beef
    assert content["calories"] == meal.calories
    assert content["id"] == str(meal.id)


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
    assert content["restaurant"] == meal.restaurant
    assert content["is_vegetarian"] == meal.is_vegetarian
    assert content["is_beef"] == meal.is_beef
    assert content["calories"] == meal.calories
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


def test_create_meal_with_minimum_fields(
    client: TestClient, teacher_token_headers: dict[str, str]
) -> None:
    """Test creating a meal with only required fields"""
    data = {
        "name": "Simple Meal",
        "restaurant": "Test Restaurant",
    }
    response = client.post(
        f"{settings.API_V1_STR}/meals/",
        headers=teacher_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["restaurant"] == data["restaurant"]
    assert content["description"] is None
    assert content["price"] is None
    assert content["calories"] is None
    assert content["is_vegetarian"] is False
    assert content["is_beef"] is False


def test_create_meal_invalid_price(
    client: TestClient, teacher_token_headers: dict[str, str]
) -> None:
    """Test creating a meal with invalid price"""
    data = {
        "name": "Test Meal",
        "restaurant": "Test Restaurant",
        "price": -10.50,  # Invalid negative price
    }
    response = client.post(
        f"{settings.API_V1_STR}/meals/",
        headers=teacher_token_headers,
        json=data,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Price cannot be negative"


def test_update_meal_by_staff(
    client: TestClient, staff_token_headers: dict[str, str], db: Session
) -> None:
    """Test that staff can't update meals"""
    meal = create_random_meal(db)
    data = {"name": "Updated Meal"}
    response = client.put(
        f"{settings.API_V1_STR}/meals/{meal.id}",
        headers=staff_token_headers,
        json=data,
    )
    assert response.status_code == 403
    assert (
        response.json()["detail"] == "Only teachers and admins can access this resource"
    )


def test_update_meal_partial(
    client: TestClient, teacher_token_headers: dict[str, str], db: Session
) -> None:
    """Test updating only some fields of a meal"""
    meal = create_random_meal(db)
    original_description = meal.description
    data = {"name": "Updated Name Only"}
    response = client.put(
        f"{settings.API_V1_STR}/meals/{meal.id}",
        headers=teacher_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == "Updated Name Only"
    assert content["description"] == original_description


def test_read_meals_pagination(
    client: TestClient, teacher_token_headers: dict[str, str], db: Session
) -> None:
    """Test pagination of meals list"""
    # Create multiple meals
    for _ in range(3):
        create_random_meal(db)

    # Test with limit
    response = client.get(
        f"{settings.API_V1_STR}/meals/?limit=2",
        headers=teacher_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content) == 2

    # Test with skip
    response = client.get(
        f"{settings.API_V1_STR}/meals/?skip=1",
        headers=teacher_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content) >= 2


def test_create_meal_invalid_calories(
    client: TestClient, teacher_token_headers: dict[str, str]
) -> None:
    """Test creating a meal with invalid calories"""
    data = {
        "name": "Test Meal",
        "restaurant": "Test Restaurant",
        "calories": -100,  # Invalid negative calories
    }
    response = client.post(
        f"{settings.API_V1_STR}/meals/",
        headers=teacher_token_headers,
        json=data,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Calories cannot be negative"


def test_delete_meal_by_student(
    client: TestClient, student_token_headers: dict[str, str], db: Session
) -> None:
    """Test that students can't delete meals"""
    meal = create_random_meal(db)
    response = client.delete(
        f"{settings.API_V1_STR}/meals/{meal.id}",
        headers=student_token_headers,
    )
    assert response.status_code == 403
    assert (
        response.json()["detail"] == "Only teachers and admins can access this resource"
    )


def test_read_meal_by_student(
    client: TestClient, student_token_headers: dict[str, str], db: Session
) -> None:
    """Test that students can read meal details"""
    meal = create_random_meal(db)
    response = client.get(
        f"{settings.API_V1_STR}/meals/{meal.id}",
        headers=student_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == str(meal.id)
    assert content["name"] == meal.name
