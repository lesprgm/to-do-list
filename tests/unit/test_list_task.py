from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.main import app
from app.api import deps
from app.db import Base


@pytest.fixture()
def client(tmp_path):
    # Temporary file-based SQLite for isolation
    db_path = tmp_path / "test_list.db"
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


def _create_task(client: TestClient, title: str, status: str, priority: str):
    payload = {"title": title, "status": status, "priority": priority}
    # status is ignored on create; using PATCH to set desired status
    resp = client.post("/v1/tasks/", json={"title": title, "priority": priority})
    assert resp.status_code == 201, resp.text
    task = resp.json()
    # Update status if needed
    if status != task["status"]:
        r2 = client.patch(f"/v1/tasks/{task['id']}", json={"status": status})
        assert r2.status_code == 200, r2.text
        task = r2.json()
    return task


def test_list_tasks_empty(client: TestClient):
    response = client.get("/v1/tasks/")
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_with_filters(client: TestClient):
    t1 = _create_task(client, "Do homework", status="todo", priority="high")
    t2 = _create_task(client, "Clean room", status="done", priority="low")
    t3 = _create_task(client, "Buy groceries", status="todo", priority="med")

    # List all
    response = client.get("/v1/tasks/")
    assert response.status_code == 200
    data = response.json()
    ids = [t["id"] for t in data]
    assert set(ids) == {t1["id"], t2["id"], t3["id"]}

    # Filter by id
    response = client.get("/v1/tasks/", params={"task_id": t1["id"]})
    assert response.status_code == 200
    assert [t["id"] for t in response.json()] == [t1["id"]]

    # Filter by status
    response = client.get("/v1/tasks/", params={"status": "done"})
    assert response.status_code == 200
    assert [t["id"] for t in response.json()] == [t2["id"]]

    # Filter by priority
    response = client.get("/v1/tasks/", params={"priority": "high"})
    assert response.status_code == 200
    assert [t["id"] for t in response.json()] == [t1["id"]]