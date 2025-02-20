import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.db.enums import RoleType
from app.tests.utils.equipment import create_random_equipment
from app.tests.utils.event import create_random_event
from app.tests.utils.meal import create_random_meal
from app.tests.utils.user import create_random_user


def test_create_event(
    client: TestClient, teacher_token_headers: dict[str, str], db: Session
) -> None:
    # Create a test item for packing list
    equipment = create_random_equipment(db)
    coordinator = create_random_user(db, role=RoleType.STAFF)
    # Create a test meal
    meal = create_random_meal(db)

    data = {
        "name": "Test Event",
        "description": "Test Description",
        "start_date": "2024-07-01",
        "end_date": "2024-07-05",
        "coordinator_id": str(coordinator.id),
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
    assert "coordinator_id" in content
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
    assert (
        response.json()["detail"] == "Only teachers and admins can access this resource"
    )


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
    coordinator = create_random_user(db, role=RoleType.STAFF)
    data = {
        "name": "Updated Event",
        "description": "Updated Description",
        "start_date": "2024-08-01",
        "end_date": "2024-08-05",
        "coordinator_id": str(coordinator.id),
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


# Test creating an event with missing required fields
def test_create_event_missing_fields(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"description": "Missing name"}
    response = client.post(
        f"{settings.API_V1_STR}/events/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 422  # Unprocessable Entity


# Test creating an event with invalid date format
def test_create_event_invalid_date_format(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {
        "name": "Test Event",
        "start_date": "07-01-2024",  # Invalid format
        "end_date": "07-05-2024",  # Invalid format
    }
    response = client.post(
        f"{settings.API_V1_STR}/events/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 422  # Unprocessable Entity


# Test updating an event with invalid UUID
def test_update_event_invalid_uuid(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"name": "Updated Event"}
    response = client.put(
        f"{settings.API_V1_STR}/events/invalid-uuid",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 422  # Unprocessable Entity


# Test deleting an event with invalid UUID
def test_delete_event_invalid_uuid(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}/events/invalid-uuid",
        headers=superuser_token_headers,
    )
    assert response.status_code == 422  # Unprocessable Entity


# Test reading events with boundary skip and limit values
def test_read_events_boundary_values(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_random_event(db)
    response = client.get(
        f"{settings.API_V1_STR}/events/?skip=0&limit=0",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) == 0


# Test creating an event with maximum length name
def test_create_event_max_length_name(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    max_length_name = "A" * 255
    data = {
        "name": max_length_name,
        "start_date": "2024-07-01",
        "end_date": "2024-07-05",
    }
    response = client.post(
        f"{settings.API_V1_STR}/events/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 422


# Test updating an event with empty name
def test_update_event_empty_name(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    event = create_random_event(db)
    data = {"name": ""}
    response = client.put(
        f"{settings.API_V1_STR}/events/{event.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 422


# Test deleting an event with valid UUID but not existing in the database
def test_delete_event_nonexistent(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    non_existent_uuid = uuid.uuid4()
    response = client.delete(
        f"{settings.API_V1_STR}/events/{non_existent_uuid}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Event not found"


# Test creating an event with a non-existent coordinator
def test_create_event_nonexistent_coordinator(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    non_existent_coordinator_id = uuid.uuid4()
    data = {
        "name": "Event with Non-existent Coordinator",
        "start_date": "2024-07-01",
        "end_date": "2024-07-05",
        "coordinator_id": str(non_existent_coordinator_id),
    }
    response = client.post(
        f"{settings.API_V1_STR}/events/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == f"User with id {non_existent_coordinator_id} not found"
