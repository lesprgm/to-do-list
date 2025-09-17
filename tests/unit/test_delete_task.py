import pytest
from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)

def test_delete_task_success(monkeypatch):
    # Fake service layer behavior: return True when task exists
    def fake_delete_task(db, task_id: int):
        return True

    # Patch the actual delete service
    from app.services import tasks
    monkeypatch.setattr(tasks, "delete_task", fake_delete_task)

    response = client.delete("/v1/tasks/1")
    assert response.status_code == 204
    assert response.content == b""  # No response body for 204


def test_delete_task_not_found(monkeypatch):
    # Fake service layer behavior: return False when task does not exist
    def fake_delete_task(db, task_id: int):
        return False

    from app.services import tasks
    monkeypatch.setattr(tasks, "delete_task", fake_delete_task)

    response = client.delete("/v1/tasks/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
