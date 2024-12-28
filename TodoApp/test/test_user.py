from .utils import *
from ..routers.user import get_db, get_current_user
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_return_user():
    response = client.get("/user/")
    assert (
        response.status_code == status.HTTP_200_OK
    ), f"Unexpected status code: {response.status_code}"
    user_data = response.json()
    assert "email" in user_data, f"Email not found in response: {user_data}"
    assert (
        user_data["email"] == "test@example.com"
    ), f"Unexpected email: {user_data['email']}"
