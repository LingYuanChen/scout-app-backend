from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete, select

from app.core.config import settings
from app.core.db import engine, init_db
from app.db import (
    Attendance,
    Equipment,
    Event,
    EventMealOption,
    Meal,
    MealChoice,
    PackingEquipment,
    User,
)
from app.main import app
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import get_superuser_token_headers


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        init_db(session)
        yield session
        # List of models to delete
        models_to_delete = [
            PackingEquipment,
            MealChoice,
            EventMealOption,
            Attendance,
            Equipment,
            Event,
            Meal,
            User,
        ]
        # Delete each model
        for model in models_to_delete:
            session.execute(delete(model))
        session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    """Return a valid token for superuser"""
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def teacher_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    """Return a valid token for teacher user"""
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_TEACHER, db=db, role="teacher"
    )


@pytest.fixture(scope="module")
def student_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    """Return a valid token for student user"""
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_STUDENT, db=db, role="student"
    )


@pytest.fixture(autouse=True)
def reset_superuser_password(db: Session) -> Generator[None, None, None]:
    # Let the test run
    yield

    # After test: Reset password
    from app.core.security import get_password_hash

    user_query = select(User).where(User.email == settings.FIRST_SUPERUSER)
    superuser = db.exec(user_query).first()
    if superuser:
        superuser.hashed_password = get_password_hash(settings.FIRST_SUPERUSER_PASSWORD)
        db.commit()
