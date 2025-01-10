from typing import Literal

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import User, UserCreate, UserUpdate
from app.tests.utils.utils import random_email, random_lower_string

# Define valid role types
UserRole = Literal["superuser", "teacher", "student"]


def user_authentication_headers(
    *, client: TestClient, email: str, password: str
) -> dict[str, str]:
    data = {"username": email, "password": password}

    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def create_random_user(
    db: Session,
    *,
    role: UserRole = "student",
    is_active: bool = True,
) -> User:
    """Create a random user with specified role.

    Args:
        db: Database session
        role: User role ("superuser", "teacher", "student")
        is_active: If True, user is active

    Returns:
        Created user
    """
    email = random_email()
    password = random_lower_string()

    user_in = UserCreate(
        email=email,
        password=password,
        is_superuser=(role == "superuser"),
        is_active=is_active,
        role=role,
    )
    user = crud.create_user(session=db, user_create=user_in)
    return user


def authentication_token_from_email(
    *,
    client: TestClient,
    email: str,
    db: Session,
    role: UserRole = "student",
    is_active: bool = True,
) -> dict[str, str]:
    """
    Return a valid token for the user with given email.
    If the user doesn't exist it is created first.

    Args:
        client: TestClient instance
        email: User email
        db: Database session
        role: User role ("superuser", "teacher", "student")
        is_active: If True, user is active
    """
    password = random_lower_string()
    user = crud.get_user_by_email(session=db, email=email)
    if not user:
        user_in_create = UserCreate(
            email=email,
            password=password,
            is_superuser=(role == "superuser"),
            is_active=is_active,
            role=role,
        )
        user = crud.create_user(session=db, user_create=user_in_create)
    else:
        user_in_update = UserUpdate(password=password)
        user = crud.update_user(session=db, db_user=user, user_in=user_in_update)

    return user_authentication_headers(client=client, email=email, password=password)


def create_random_superuser(db: Session) -> User:
    """Convenience function to create a superuser"""
    return create_random_user(db, role="superuser")


def create_random_teacher(db: Session) -> User:
    """Convenience function to create a teacher"""
    return create_random_user(db, role="teacher")


def create_random_student(db: Session) -> User:
    """Convenience function to create a student"""
    return create_random_user(db, role="student")
