from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
)
from starlette import status
from ..models import Todo
from ..database import SessionLocal
from .auth import get_current_user

router = APIRouter(
    prefix="/todos",
    tags=["Todos"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=200)
    priority: int = Field(..., gt=0, lt=6)
    complete: bool = Field(default=False)


class TodoUpdate(BaseModel):
    title: str = Field(None, min_length=1, max_length=100)
    description: str = Field(None, min_length=1, max_length=200)
    priority: int = Field(None, gt=0, lt=6)
    complete: bool = Field(default=False)

    class Config:
        from_attributes = True


class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: int
    complete: bool
    owner_id: int

    class Config:
        from_attributes = True


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[TodoResponse])
async def read_all_todos(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return [
        TodoResponse.model_validate(todo)
        for todo in db.query(Todo).filter(Todo.owner_id == user.get("id")).all()
    ]


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def read_todo(
    user: user_dependency,
    db: db_dependency,
    id: int = Path(..., gt=0, title="ID of the todo you're looking for"),
) -> TodoResponse:
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    todo_model = (
        db.query(Todo)
        .filter(Todo.id == id)
        .filter(Todo.owner_id == user.get("id"))
        .first()
    )
    if not todo_model:
        raise HTTPException(status_code=404, detail="Todo not found")
    return TodoResponse.model_validate(todo_model)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(
    user: user_dependency,
    db: db_dependency,
    todo_in: TodoCreate,
) -> TodoResponse:
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    new_todo = Todo(**todo_in.model_dump(), owner_id=user["id"])
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return TodoResponse.model_validate(new_todo)


@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=TodoResponse)
async def update_todo(
    user: user_dependency,
    db: db_dependency,
    todo_update: TodoUpdate,
    id: int = Path(..., gt=0, title="ID of the todo you're updating"),
) -> TodoResponse:
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    todo_model = (
        db.query(Todo)
        .filter(Todo.id == id)
        .filter(Todo.owner_id == user.get("id"))
        .first()
    )
    if not todo_model:
        raise HTTPException(status_code=404, detail="Todo not found")
    update_data = todo_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(todo_model, key, value)
    db.commit()
    db.refresh(todo_model)
    return TodoResponse.model_validate(todo_model)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency,
    db: db_dependency,
    id: int = Path(..., gt=0, title="ID of the todo you're deleting"),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    todo_model = (
        db.query(Todo)
        .filter(Todo.id == id)
        .filter(Todo.owner_id == user.get("id"))
        .first()
    )
    if not todo_model:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo_model)
    db.commit()
