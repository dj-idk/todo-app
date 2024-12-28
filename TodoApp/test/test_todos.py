from ..routers.todo import get_db, get_current_user
from fastapi import status
from .utils import *


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_authenticated(test_todo):
    response = client.get("/todos/")
    assert response.status_code == status.HTTP_200_OK
    todos = response.json()
    assert len(todos) == 1


def test_read_one_authenticated(test_todo):
    response = client.get(f"/todos/{test_todo.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": test_todo.id,
        "title": "Test Todo",
        "description": "Test Description",
        "priority": 1,
        "complete": False,
        "owner_id": 1,
    }


def test_read_one_authenticated_not_found():
    response = client.get("/todos/100")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_todo(test_todo):
    response = client.post(
        "/todos/",
        json={
            "title": "Test Todo 2",
            "description": "Test Description 2",
            "priority": 2,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED

    created_todo = response.json()
    assert created_todo["title"] == "Test Todo 2"
    assert created_todo["description"] == "Test Description 2"
    assert created_todo["priority"] == 2
    assert created_todo["complete"] == False
    assert created_todo["owner_id"] == 1
    assert "id" in created_todo


def test_update_todo(test_todo):
    response = client.put(
        f"/todos/{test_todo.id}",
        json={
            "title": "Updated Test Todo",
            "description": "Updated Test Description",
            "priority": 3,
            "complete": True,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    updated_todo = response.json()
    assert updated_todo["id"] == test_todo.id
    assert updated_todo["title"] == "Updated Test Todo"
    assert updated_todo["description"] == "Updated Test Description"
    assert updated_todo["priority"] == 3
    assert updated_todo["complete"] == True
    assert updated_todo["owner_id"] == 1
    assert "id" in updated_todo
    assert updated_todo["title"] != test_todo.title
    assert updated_todo["description"] != test_todo.description
    assert updated_todo["priority"] != test_todo.priority
    assert updated_todo["complete"] != test_todo.complete
