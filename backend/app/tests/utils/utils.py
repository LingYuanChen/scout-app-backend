import random
import string
import uuid

from fastapi.testclient import TestClient

from app.core.config import settings


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def get_superuser_token_headers(client: TestClient) -> dict[str, str]:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


def get_user_id_from_token(
    client: TestClient, token_headers: dict[str, str]
) -> uuid.UUID:
    """Get user ID using the /users/me endpoint

    Args:
        client: TestClient instance
        token_headers: Headers containing Bearer token

    Returns:
        user_id: UUID string of the user
    """
    response = client.get(f"{settings.API_V1_STR}/users/me", headers=token_headers)
    current_user = response.json()
    return uuid.UUID(current_user["id"])
