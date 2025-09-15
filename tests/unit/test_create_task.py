from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.main import app
from app.api import deps
from app.db import Base
from app.db.models import Task


@pytest.fixture()
def client(tmp_path):
    # Use a temporary file-based SQLite database for tests
    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite+pysqlite:///{db_path}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[deps.get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def test_create_task_happy_path(client: TestClient):
    payload = {
        "title": "Buy milk",
        "description": "2% organic",
        "priority": "high",
        "tags": ["groceries", "errands"],
        "due_date": datetime(2025, 9, 15, 12, 0, tzinfo=timezone.utc).isoformat(),
    }
    resp = client.post("/v1/tasks/", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["id"] >= 1
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["status"] == "todo"
    assert data["priority"] == payload["priority"]
    assert data["tags"] == payload["tags"]
    # Accept either explicit +00:00 or Z for UTC; both are ISO-8601
    due_str = data["due_date"]
    assert due_str.startswith("2025-09-15T12:00:00")
    assert due_str.endswith("Z") or due_str.endswith("+00:00")
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.parametrize(
    "payload,expected_status",
    [
        ({"title": ""}, 422),  # empty title
        ({"title": "   "}, 422),
        ({"title": "Test", "priority": "invalid"}, 422),
        ({"title": "Test", "due_date": "2025-09-15T12:00:00"}, 422),  # no tz
        ({"title": "Test", "due_date": "not-a-date"}, 422),
    ],
)
def test_create_task_validation_errors(client: TestClient, payload, expected_status):
    resp = client.post("/v1/tasks/", json=payload)
    assert resp.status_code == expected_status
    # Should be JSON with detail
    body = resp.json()
    assert "detail" in body
