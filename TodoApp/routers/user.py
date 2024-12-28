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
from ..models import User
from ..database import SessionLocal
from .auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(
    prefix="/user",
    tags=["User Management"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    username: str = Field(None)
    email: str = Field(None)
    first_name: str = Field(None)
    last_name: str = Field(None)
    phone_number: str = Field(None)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return db.query(User).filter_by(id=user.get("id")).first()


@router.put("/password", status_code=status.HTTP_200_OK)
async def update_password(
    user: user_dependency,
    db: db_dependency,
    user_verification: UserVerification,
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    if not bcrypt_context.verify(
        user_verification.password, user_model.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Error: Incorrect password"
        )
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()


@router.put("/update-profile", status_code=status.HTTP_200_OK)
async def update_profile(
    db: db_dependency, user: user_dependency, user_update: UserUpdate
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user_model, key, value)
    db.add(user_model)
    db.commit()
