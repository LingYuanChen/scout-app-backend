import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils.equipment import create_random_equipment


def test_create_equipment(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "Foo", "description": "Fighters"}
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
    assert "owner_id" in content


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
    assert content["owner_id"] == str(equipment.owner_id)


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
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


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
    assert content["owner_id"] == str(equipment.owner_id)


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
    assert content["detail"] == "Not enough permissions"


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
    assert content["detail"] == "Not enough permissions"
