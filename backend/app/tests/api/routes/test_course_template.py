import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.db import CourseTemplate, User
from app.db.enums import RoleType


def test_create_course_template(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {
        "name": "帳篷競賽",
        "description": "測試用的帳篷競賽課程",
        "time_required": 3.5,
        "location": "台北",
        "equipments": [],
    }
    response = client.post(
        f"{settings.API_V1_STR}/course_templates/",
        json=data,
        headers=superuser_token_headers,
    )

    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["description"] == data["description"]
    assert content["time_required"] == data["time_required"]
    assert content["location"] == data["location"]
    assert "created_by" in content


def test_read_course_templates(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/course_templates/", headers=superuser_token_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_course_template(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # 先創建一個課程模板
    user = db.exec(
        select(User).where(User.role_type == RoleType.ADMIN)
    ).first()  # 確保使用管理員使用者
    if not user:
        user = User(
            id=uuid.uuid4(),
            email="admin@example.com",
            hashed_password="fakepassword",
            full_name="Admin User",
            role_type=RoleType.ADMIN,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    course = CourseTemplate(
        id=uuid.uuid4(),
        name="原始名稱",
        description="原始描述",
        time_required=2.0,
        location="原始地點",
        created_by=user.id,  # 改用 created_by
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    update_data = {"name": "更新後名稱", "description": "更新後描述"}
    response = client.put(
        f"{settings.API_V1_STR}/course_templates/{course.id}",
        json=update_data,
        headers=superuser_token_headers,
    )

    assert response.status_code == 200
    content = response.json()
    assert content["name"] == update_data["name"]
    assert content["description"] == update_data["description"]


def test_delete_course_template(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/course_templates/", headers=superuser_token_headers
    )
    if response.json():
        for course_template in response.json():
            course_id = course_template["id"]
            response = client.delete(
                f"{settings.API_V1_STR}/course_templates/{course_id}",
                headers=superuser_token_headers,
            )

        assert response.status_code == 200
        assert response.json()["message"] == "Course template is deleted"
    else:
        data = {
            "name": "帳篷競賽",
            "description": "測試用的帳篷競賽課程",
            "time_required": 3.5,
            "location": "台北",
            "equipments": [],
        }
        response = client.post(
            f"{settings.API_V1_STR}/course_templates/",
            json=data,
            headers=superuser_token_headers,
        )
        assert response.status_code == 200
        course_id = response.json()["id"]
        response = client.delete(
            f"{settings.API_V1_STR}/course_templates/{course_id}",
            headers=superuser_token_headers,
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Course template is deleted"
