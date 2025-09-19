from fastapi.testclient import TestClient
import pytest
from fastapi import FastAPI
from app.api.routers import list_tasks as lt
from app.api.routers import update_tasks
import json

app = FastAPI()
app.include_router(lt.router)

client = TestClient(app)

def test_update_task_partial(tmp_path, monkeypatch):
    tasks_file = tmp_path / "tasks.json"
    monkeypatch.setattr("app.api.routers.list_tasks.TASKS_FILE", str(tasks_file))

    test_data = [
        
        {"task_id": "1",
         "title": "Do homework",
         "description": "Math",
         "status": "pending",
         "priority": "high"
         },
         {
            "task_id": "2",
            "title": "Clean room",
            "description": "Living room",
            "status": "done",
            "priority": "low"
        }]

    with open(tasks_file, 'w') as f:
        json.dump(test_data, f)

        # Partial Update: only status 
    response = client.patch("/update_tasks/1", params={"status": "done"})
    assert response.status_code == 200
    updated_task = json.load(open(tasks_file))
    assert updated_task[0]["status"] == "done"

        # Partial Update: title and priority
    response = client.patch("/update_tasks/1", params={"title": "Homework updated", "priority": "medium"})
    assert response.status_code == 200
    updated_task = json.load(open(tasks_file))
    assert updated_task[0]["title"] == "Homework updated"
    assert updated_task[0]["priority"] == "medium"

def test_update_task_invalid(tmp_path, monkeypatch):

    tasks_file = tmp_path /"tasks.json"
    monkeypatch.setattr("app.api.routers.list_tasks.TASKS_FILE", str(tasks_file))

    test_data = [
        {"task_id": "1",
         "title" : "Do homework",
         "description": "Math",
         "status": "pending",
         "priority" : "high"
         },
    ]
    with open(tasks_file, 'w') as f:
        json.dump(test_data, f)
        
    response = client.patch("/update_tasks/1", params={"status": "ienfuenfnef"})
    assert response.status_code == 422
    body = response.json()
    assert "status" in json.dumps(body).lower() or "invalid" in json.dumps(body).lower()

def test_update_task_missing(tmp_path, monkeypatch):
    tasks_file = tmp_path / "tasks.json"
    monkeypatch.setattr("app.api.routers.list_tasks.TASKS_FILE", str(tasks_file))

    test_data = [
        {"task_id": "1",
         "title": "Do homework",
         "status": "pending",
         "priority": "high"}
    ]
    with open(tasks_file, 'w') as f:
        json.dump(test_data, f)
    
    response = client.patch("/update_tasks/2", params={"status": "done"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}



    
        

    