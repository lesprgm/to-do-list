from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Simple SQLite setup for local dev and tests. Tests will override this via dependency overrides.
SQLALCHEMY_DATABASE_URL = "sqlite:///./todo.db"

# check_same_thread=False is required for SQLite when used with FastAPI/TestClient
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
