from __future__ import annotations
import os
from typing import Optional, Literal, List, Dict, Any

import requests
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("to-do-list")


BASE_URL = os.getenv("TODO_API_BASE_URL", "http://127.0.0.1:8000")
TASKS_PATH = "/v1/tasks/" 


@mcp.tool(title="List Tasks", description="List tasks with optional filters. Returns structured JSON.")
def list_tasks(
    status: Optional[str] = None,
    priority: Optional[Literal["low", "med", "high"]] = None,
    tag: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    if status:
        params["status"] = status
    if priority:
        params["priority"] = priority
    if tag:
        params["tag"] = tag
    if limit is not None:
        params["limit"] = int(limit)
    if offset is not None:
        params["offset"] = int(offset)

    url = f"{BASE_URL}{TASKS_PATH}"
    resp = requests.get(url, params=params, timeout=15)
    try:
        data = resp.json()
    except Exception:
        data = {"message": resp.text}

    return {
        "ok": resp.ok,
        "status": resp.status_code,
        "url": resp.url,
        "data": data,
    }


@mcp.tool(title="Create Task", description="Create a new task via POST /v1/tasks. Returns structured JSON.")
def create_task(
    title: str,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: Optional[Literal["low", "med", "high"]] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"title": title}
    if description is not None:
        payload["description"] = description
    if due_date is not None:
        payload["due_date"] = due_date
    if priority is not None:
        payload["priority"] = priority
    if tags is not None:
        payload["tags"] = tags

    url = f"{BASE_URL}{TASKS_PATH}"
    resp = requests.post(url, json=payload, timeout=15)
    try:
        data = resp.json()
    except Exception:
        data = {"message": resp.text}

    return {
        "ok": resp.status_code == 201,
        "status": resp.status_code,
        "url": url,
        "data": data,
    }


@mcp.tool(title="Update Task", description="Update fields on a task via PATCH /v1/tasks/{task_id}. Returns structured JSON.")
def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[str] = None,  
    priority: Optional[Literal["low", "med", "high"]] = None,
    status: Optional[Literal["todo", "in_progress", "done"]] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    # Build a partial update payload with only provided fields
    payload: Dict[str, Any] = {}
    if title is not None:
        payload["title"] = title
    if description is not None:
        payload["description"] = description
    if due_date is not None:
        payload["due_date"] = due_date
    if priority is not None:
        payload["priority"] = priority
    if status is not None:
        payload["status"] = status
    if tags is not None:
        payload["tags"] = tags

    if not payload:
        return {
            "ok": False,
            "status": 400,
            "url": f"{BASE_URL}{TASKS_PATH}{task_id}",
            "data": {"detail": "No fields provided to update"},
        }

    url = f"{BASE_URL}{TASKS_PATH}{int(task_id)}"
    resp = requests.patch(url, json=payload, timeout=15)
    try:
        data = resp.json()
    except Exception:
        data = {"message": resp.text}

    return {
        "ok": resp.ok,
        "status": resp.status_code,
        "url": url,
        "data": data,
    }


@mcp.tool(title="Delete Task", description="Delete a task via DELETE /v1/tasks/{task_id}. Returns structured JSON.")
def delete_task(task_id: int) -> Dict[str, Any]:
    url = f"{BASE_URL}{TASKS_PATH}{int(task_id)}"
    resp = requests.delete(url, timeout=15)
    try:
        # Some APIs return JSON body; others return 204 with no body
        data = resp.json()
    except Exception:
        data = {"message": "No Content" if resp.status_code == 204 else resp.text}

    return {
        "ok": resp.status_code in (200, 202, 204),
        "status": resp.status_code,
        "url": url,
        "data": data,
    }


if __name__ == "__main__":
    mcp.run()
