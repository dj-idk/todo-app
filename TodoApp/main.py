from fastapi import FastAPI
from .models import Base
from .database import engine
from .routers import auth, todo, admin, user
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {str(e)}")


@app.get("/healthy")
def health_check():
    return {"status": "Healthy"}


app.include_router(auth.router)
app.include_router(todo.router)
app.include_router(admin.router)
app.include_router(user.router)
