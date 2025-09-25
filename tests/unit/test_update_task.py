from __future__ import annotations

import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.main import app
from app.api import deps
from app.db import Base


@pytest.fixture()
def client(tmp_path):
    db_path = tmp_path / "test_update.db"
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


def test_update_task_partial(client: TestClient):
    # Create a task
    resp = client.post("/v1/tasks/", json={"title": "Do homework", "priority": "high", "description": "Math"})
    assert resp.status_code == 201, resp.text
    task = resp.json()

    # Partial update: only status
    response = client.patch(f"/v1/tasks/{task['id']}", json={"status": "done"})
    assert response.status_code == 200
    assert response.json()["status"] == "done"

    # Partial update: title and priority
    response = client.patch(f"/v1/tasks/{task['id']}", json={"title": "Homework updated", "priority": "med"})
    assert response.status_code == 200
    updated = response.json()
    assert updated["title"] == "Homework updated"
    assert updated["priority"] == "med"


def test_update_task_invalid(client: TestClient):
    # Create a task
    resp = client.post("/v1/tasks/", json={"title": "Do homework"})
    assert resp.status_code == 201
    task = resp.json()

    # Invalid status
    response = client.patch(f"/v1/tasks/{task['id']}", json={"status": "ienfuenfnef"})
    assert response.status_code == 422
    body = response.json()
    assert "detail" in body


def test_update_task_missing(client: TestClient):
    response = client.patch("/v1/tasks/99999", json={"status": "done"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}



    
        

    