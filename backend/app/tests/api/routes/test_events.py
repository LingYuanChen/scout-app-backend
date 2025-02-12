import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils.equipment import create_random_equipment
from app.tests.utils.event import create_random_event
from app.tests.utils.meal import create_random_meal


def test_create_event(
    client: TestClient, teacher_token_headers: dict[str, str], db: Session
) -> None:
    # Create a test item for packing list
    equipment = create_random_equipment(db)
    # Create a test meal
    meal = create_random_meal(db)

    data = {
        "name": "Test Event",
        "description": "Test Description",
        "start_date": "2024-07-01",
        "end_date": "2024-07-05",
        "packing_equipments": [
            {
                "equipment_id": str(equipment.id),
                "quantity": 2,
                "required": True,
                "notes": "Important",
            }
        ],
        "meal_options": [
            {
                "meal_id": str(meal.id),
                "meal_type": "breakfast",
                "day": 1,
                "max_quantity": 50,
            }
        ],
    }
    response = client.post(
        f"{settings.API_V1_STR}/events/",
        headers=teacher_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "created_by_id" in content
    assert len(content["packing_equipments"]) == 1


def test_create_event_by_student(
    client: TestClient, student_token_headers: dict[str, str]
) -> None:
    data = {
        "name": "Test Event",
        "description": "Test Description",
        "start_date": "2024-07-01",
        "end_date": "2024-07-05",
    }
    response = client.post(
        f"{settings.API_V1_STR}/events/",
        headers=student_token_headers,
        json=data,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Only teachers can create events"


def test_read_event(
    client: TestClient, teacher_token_headers: dict[str, str], db: Session
) -> None:
    event = create_random_event(db)
    response = client.get(
        f"{settings.API_V1_STR}/events/{event.id}",
        headers=teacher_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == event.name
    assert content["description"] == event.description
    assert content["id"] == str(event.id)


def test_read_event_not_found(
    client: TestClient, teacher_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/events/{uuid.uuid4()}",
        headers=teacher_token_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


def test_read_events(
    client: TestClient, teacher_token_headers: dict[str, str], db: Session
) -> None:
    create_random_event(db)
    create_random_event(db)
    response = client.get(
        f"{settings.API_V1_STR}/events/",
        headers=teacher_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2
    assert "count" in content


def test_update_event(
    client: TestClient, teacher_token_headers: dict[str, str], db: Session
) -> None:
    event = create_random_event(db)
    equipment = create_random_equipment(db)

    data = {
        "name": "Updated Event",
        "description": "Updated Description",
        "start_date": "2024-08-01",
        "end_date": "2024-08-05",
        "packing_equipments": [
            {"equipment_id": str(equipment.id), "quantity": 1, "required": True}
        ],
    }
    response = client.put(
        f"{settings.API_V1_STR}/events/{event.id}",
        headers=teacher_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["description"] == data["description"]
    assert len(content["packing_equipments"]) == 1


def test_delete_event(
    client: TestClient, teacher_token_headers: dict[str, str], db: Session
) -> None:
    event = create_random_event(db)
    response = client.delete(
        f"{settings.API_V1_STR}/events/{event.id}",
        headers=teacher_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Event deleted"
