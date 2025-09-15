from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy.orm import Session

from app.db import SessionLocal, Base, engine
from app.db.models import Task  # ensure models are imported for table creation


# Create tables at import time for simplicity; for real apps use Alembic migrations.
Base.metadata.create_all(bind=engine)


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
