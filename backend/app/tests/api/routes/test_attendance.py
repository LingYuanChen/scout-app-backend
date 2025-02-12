from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils.attendance import (
    clean_attendance_tables,
    create_attendance_with_packing_equipments,
    create_random_attendance,
)
from app.tests.utils.event import create_random_event
from app.tests.utils.utils import get_user_id_from_token


def test_join_event(
    client: TestClient, student_token_headers: dict[str, str], db: Session
) -> None:
    event = create_random_event(db)
    response = client.post(
        f"{settings.API_V1_STR}/attendance/{event.id}/join",
        headers=student_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Successfully joined the event"


def test_join_event_already_attending(
    client: TestClient, student_token_headers: dict[str, str], db: Session
) -> None:
    user_id = get_user_id_from_token(client, student_token_headers)
    attendance = create_random_attendance(db, user_id=user_id)

    response = client.post(
        f"{settings.API_V1_STR}/attendance/{attendance.event_id}/join",
        headers=student_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Already attending this event"


def test_leave_event(
    client: TestClient, student_token_headers: dict[str, str], db: Session
) -> None:
    user_id = get_user_id_from_token(client, student_token_headers)
    attendance = create_random_attendance(db, user_id=user_id)

    response = client.post(
        f"{settings.API_V1_STR}/attendance/{attendance.event_id}/leave",
        headers=student_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Successfully left the event"


def test_leave_event_not_attending(
    client: TestClient, student_token_headers: dict[str, str], db: Session
) -> None:
    event = create_random_event(db)
    response = client.post(
        f"{settings.API_V1_STR}/attendance/{event.id}/leave",
        headers=student_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Not attending this event"


def test_get_my_events(
    client: TestClient, student_token_headers: dict[str, str], db: Session
) -> None:
    clean_attendance_tables(db)
    user_id = get_user_id_from_token(client, student_token_headers)
    # Create two attendances for the user
    create_random_attendance(db, user_id=user_id)
    create_random_attendance(db, user_id=user_id)

    response = client.get(
        f"{settings.API_V1_STR}/attendance/my-events",
        headers=student_token_headers,
    )
    assert response.status_code == 200
    events = response.json()
    assert len(events) >= 2
    # Verify event structure
    for event in events:
        assert "id" in event
        assert "name" in event
        assert "description" in event
        assert "start_date" in event
        assert "end_date" in event


def test_get_event_packing_list(
    client: TestClient, student_token_headers: dict[str, str], db: Session
) -> None:
    user_id = get_user_id_from_token(client, student_token_headers)
    attendance = create_attendance_with_packing_equipments(
        db, user_id=user_id, num_equipments=3
    )

    response = client.get(
        f"{settings.API_V1_STR}/attendance/{attendance.event_id}/packing-list",
        headers=student_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert "data" in content
    assert "count" in content
    assert content["count"] >= 1
    assert len(content["data"]) >= 1
    # Verify packing item structure
    equipment_data = content["data"][0]
    assert "equipment" in equipment_data
    assert "quantity" in equipment_data
    assert "required" in equipment_data


def test_get_event_packing_list_not_attending(
    client: TestClient, student_token_headers: dict[str, str], db: Session
) -> None:
    event = create_random_event(db)
    response = client.get(
        f"{settings.API_V1_STR}/attendance/{event.id}/packing-list",
        headers=student_token_headers,
    )
    assert response.status_code == 403
    assert (
        response.json()["detail"] == "Must be attending the event to view packing list"
    )


def test_get_my_packing_lists(
    client: TestClient, student_token_headers: dict[str, str], db: Session
) -> None:
    # Clean up any existing data
    clean_attendance_tables(db)
    user_id = get_user_id_from_token(client, student_token_headers)

    # Create multiple events with packing items
    num_events = 2
    num_equipments_per_event = 3
    created_events = []

    for _ in range(num_events):
        attendance = create_attendance_with_packing_equipments(
            db, user_id=user_id, num_equipments=num_equipments_per_event
        )
        created_events.append(str(attendance.event_id))

    # Get user's packing lists
    response = client.get(
        f"{settings.API_V1_STR}/attendance/my-packing-lists",
        headers=student_token_headers,
    )

    assert response.status_code == 200
    content = response.json()

    # Verify the response structure
    assert len(content) == num_events

    for packing_list in content:
        # Verify event data
        assert packing_list["event_id"] in created_events
        assert "event_name" in packing_list

        # Verify items data
        assert "equipments" in packing_list
        equipments = packing_list["equipments"]
        assert equipments["count"] == num_equipments_per_event
        assert len(equipments["data"]) == num_equipments_per_event

        # Verify structure of each item
        for equipment in equipments["data"]:
            assert "equipment" in equipment
            assert "quantity" in equipment
            assert "required" in equipment


def test_get_my_packing_lists_no_events(
    client: TestClient, student_token_headers: dict[str, str], db: Session
) -> None:
    """Test when user has no events"""
    clean_attendance_tables(db)
    response = client.get(
        f"{settings.API_V1_STR}/attendance/my-packing-lists",
        headers=student_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content) == 0


def test_get_my_packing_lists_no_equipments(
    client: TestClient, student_token_headers: dict[str, str], db: Session
) -> None:
    """Test when events have no packing equipments"""
    user_id = get_user_id_from_token(client, student_token_headers)
    _ = create_random_attendance(db, user_id=user_id)  # No packing equipments

    response = client.get(
        f"{settings.API_V1_STR}/attendance/my-packing-lists",
        headers=student_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content[0]["equipments"]["count"] == 0
    assert len(content[0]["equipments"]["data"]) == 0
