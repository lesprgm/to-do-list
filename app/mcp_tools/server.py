from __future__ import annotations

import os
from typing import Optional, Literal, List, Dict, Any

import requests
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("to-do-list")


BASE_URL = os.getenv("TODO_API_BASE_URL", "http://127.0.0.1:8000")
TASKS_PATH = "/v1/tasks/"  # trailing slash matches router


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
    due_date: Optional[str] = None,  # ISO-8601 UTC, e.g., 2025-09-15T12:00:00Z
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


if __name__ == "__main__":
    # Run as an MCP server over stdio
    mcp.run()
