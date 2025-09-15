from fastapi.testclient import TestClient
import pytest_
from fastapi import FastAPI
from list_tasks import router
import json

app = FastAPI()
app.include_router(router)

client = TestClient(app)

def test_list_tasks_empty(tmp_path, monkeypatch):
    # Use a temporary file for tasks.json
    tasks_file = tmp_path / "tasks.json"
    monkeypatch.setattr("list_tasks.TASKS_FILE", str(tasks_file))

    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []

def test_list_tasks_with_data(tmp_path, monkeypatch):
    test_file = tmp_path / "tasks.json"
    monkeypatch.setattr("list_tasks.TASKS_FILE", str(test_file))

    test_data = [
        {"id": 1, "title": "Do homework", "owner_id": "1", "status": "pending", "priority": "high"},
        {"id": 2, "title": "Clean room", "owner_id": "2", "status": "done", "priority": "low"},
        {"id": 3, "title": "Buy groceries", "owner_id": "1", "status": "pending", "priority": "medium"},
    ]
    with open(test_file, 'w') as f:
        json.dump(test_data, f)

    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == test_data

    # Filter by id
    response = client.get("/tasks", params={'owner_id' : '1'})
    assert response.status_code == 200
    assert response.json() == [test_data[0], test_data[2]]

    # Filter by status
    response = client.get("/tasks", params={'status' : 'done'})
    assert response.status_code == 200
    assert response.json() == [test_data[1]]

    # Filter by priority
    response = client.get("/tasks", params={'priority' : 'high'})
    assert response.status_code == 200
    assert response.json() == [test_data[0]]