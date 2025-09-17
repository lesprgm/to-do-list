from mcp.server.fastmcp import FastMCP
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, Query, APIRouter
import uvicorn
import json
import os

router = APIRouter()


TASKS_FILE = "tasks.json"

def load_tasks() -> List[dict]:
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, 'r') as f:
        return json.load(f)
def save_tasks(tasks: List[dict]):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)

@router.get("/tasks")
def list_tasks(
    owner_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
):
    tasks = load_tasks()

    if owner_id is not None:
        tasks = [t for t in tasks if t["owner_id"] == owner_id]

    if status is not None:
        tasks = [t for t in tasks if t["status"] == status]
    
    if priority is not None:
        tasks = [t for t in tasks if t["priority"] == priority]

    if search is not None:
        tasks = [t for t in tasks if search.lower() in t["title"].lower()]
        
    tasks = tasks[offset : offset + limit]
    return tasks


    