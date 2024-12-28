from .utils import *
from ..routers.admin import get_db, get_current_user
from fastapi import status
from ..models import Todo


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_admin_read_all_authenticated(test_todo):
    response = client.get("/admin/todo")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "id": test_todo.id,
            "title": "Test Todo",
            "description": "Test Description",
            "priority": 1,
            "complete": False,
            "owner_id": 1,
        }
    ]


def test_admin_delete_todo(test_todo):
    response = client.delete(f"/admin/todo/{test_todo.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert (
        TestingSessionLocal().query(Todo).filter(Todo.id == test_todo.id).first()
        is None
    )


def test_admin_delete_todo_not_found(test_todo):
    response = client.delete("/admin/todo/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
