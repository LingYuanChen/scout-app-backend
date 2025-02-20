import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils.equipment import create_random_equipment


def test_create_equipment(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {
        "title": "Foo",
        "description": "Fighters",
        "category": "Bar",
        "location": "Baz",
    }
    response = client.post(
        f"{settings.API_V1_STR}/equipments/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert "id" in content


def test_read_equipment(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    equipment = create_random_equipment(db)
    response = client.get(
        f"{settings.API_V1_STR}/equipments/{equipment.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == equipment.title
    assert content["description"] == equipment.description
    assert content["id"] == str(equipment.id)


def test_read_equipment_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/equipments/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Equipment not found"


def test_read_equipment_not_enough_permissions(
    client: TestClient, student_token_headers: dict[str, str], db: Session
) -> None:
    equipment = create_random_equipment(db)
    response = client.get(
        f"{settings.API_V1_STR}/equipments/{equipment.id}",
        headers=student_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Only teachers and admins can access this resource"


def test_read_equipments(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_random_equipment(db)
    create_random_equipment(db)
    response = client.get(
        f"{settings.API_V1_STR}/equipments/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2


def test_update_equipment(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    equipment = create_random_equipment(db)
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/equipments/{equipment.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert content["id"] == str(equipment.id)


def test_update_equipment_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/equipments/{uuid.uuid4()}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Equipment not found"


def test_update_equipment_not_enough_permissions(
    client: TestClient, student_token_headers: dict[str, str], db: Session
) -> None:
    equipment = create_random_equipment(db)
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/equipments/{equipment.id}",
        headers=student_token_headers,
        json=data,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Only teachers and admins can access this resource"


def test_delete_equipment(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    equipment = create_random_equipment(db)
    response = client.delete(
        f"{settings.API_V1_STR}/equipments/{equipment.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Equipment deleted successfully"


def test_delete_equipment_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}/equipments/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Equipment not found"


def test_delete_equipment_not_enough_permissions(
    client: TestClient, student_token_headers: dict[str, str], db: Session
) -> None:
    equipment = create_random_equipment(db)
    response = client.delete(
        f"{settings.API_V1_STR}/equipments/{equipment.id}",
        headers=student_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Only teachers and admins can access this resource"


# Test creating equipment with missing required fields
def test_create_equipment_missing_fields(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"description": "Missing title"}
    response = client.post(
        f"{settings.API_V1_STR}/equipments/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 422  # Unprocessable Entity


# Test creating equipment with invalid data types
def test_create_equipment_invalid_data_type(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": 123, "description": "Invalid title type"}
    response = client.post(
        f"{settings.API_V1_STR}/equipments/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 422  # Unprocessable Entity


# Test updating equipment with invalid UUID
def test_update_equipment_invalid_uuid(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/equipments/invalid-uuid",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 422  # Unprocessable Entity


# Test deleting equipment with invalid UUID
def test_delete_equipment_invalid_uuid(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}/equipments/invalid-uuid",
        headers=superuser_token_headers,
    )
    assert response.status_code == 422  # Unprocessable Entity


# Test reading equipment with boundary skip and limit values
def test_read_equipments_boundary_values(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_random_equipment(db)
    response = client.get(
        f"{settings.API_V1_STR}/equipments/?skip=0&limit=0",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) == 0


# Test creating equipment with maximum length title
def test_create_equipment_max_length_title(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    max_length_title = "A" * 255
    max_length_category = "B" * 100
    max_length_location = "C" * 100
    data = {
        "title": max_length_title,
        "description": "Max length title",
        "category": max_length_category,
        "location": max_length_location,
    }
    response = client.post(
        f"{settings.API_V1_STR}/equipments/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == max_length_title


# Test updating equipment with empty title
def test_update_equipment_empty_title(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    equipment = create_random_equipment(db)
    data = {"title": "", "description": "Empty title"}
    response = client.put(
        f"{settings.API_V1_STR}/equipments/{equipment.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 422  # Unprocessable Entity


# Test deleting equipment with valid UUID but not existing in the database
def test_delete_equipment_nonexistent(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    non_existent_uuid = uuid.uuid4()
    response = client.delete(
        f"{settings.API_V1_STR}/equipments/{non_existent_uuid}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Equipment not found"
