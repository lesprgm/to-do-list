# PATCH /v1/tasks/{id} accepts any subset of fields: {title?, description?, due_date?, priority?, tags?, status?}

# Enforce status values only (no transition rules yet).

# Returns updated resource 200; updated_at changes.

# 400/422 on invalid fields; 404 if missing.

# Unit tests: partial updates, invalid payloads.

from fastapi import APIRouter, HTTPException
from typing import Optional
from fastapi.responses import JSONResponse
import json
from app.api.routers import list_tasks as lt

router = lt.router

ALLOWED_STATUS = {"pending", "in_progress", "done"}

@router.patch("/update_tasks/{task_id}")
def update_task(
    task_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    ):

    if status is not None and status not in ALLOWED_STATUS:
        raise HTTPException(status_code=422, detail=f"Invalid status. Must be one of: {','.join(ALLOWED_STATUS)}")

    tasks = lt.load_tasks()
    for task in tasks:
        if task["task_id"] == task_id:
            if status is not None:
                task["status"] = status
            if priority is not None:
                task["priority"] = priority
            if title is not None:
                task["title"] = title
            if description is not None:
                task["description"] = description
            lt.save_tasks(tasks)
            return tasks
        
    raise HTTPException(status_code=404, detail="Not Found")