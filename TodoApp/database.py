from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# Get the directory of the current file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Use the /data directory on Railway, otherwise use a local directory
if os.environ.get("RAILWAY_ENVIRONMENT"):
    db_path = "/data/todosapp.db"
else:
    db_path = os.path.join(BASE_DIR, "todosapp.db")

SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Ensure the database directory exists
os.makedirs(os.path.dirname(db_path), exist_ok=True)
