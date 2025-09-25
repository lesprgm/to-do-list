from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.db.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

def delete_task(db: Session, task_id: int) -> bool:
    task = db.get(Task, task_id)
    if not task:
        return False
    try:
        db.delete(task)
        db.commit()
        return True
    except SQLAlchemyError:
        db.rollback()
        return False


def list_tasks(db: Session) -> list[Task]:
    items = db.query(Task).order_by(Task.id.asc()).all()
    for t in items:
        _normalize_task_datetimes(t)
    return items


def create_task(db: Session, payload: TaskCreate) -> Task:
    now = datetime.now(timezone.utc)
    task = Task(
        title=payload.title.strip(),
        description=payload.description,
        status="todo",
        priority=payload.priority,
        tags=payload.tags or [],
        due_date=payload.due_date,
        created_at=now,
        updated_at=now,
    )
    try:
        db.add(task)
        db.commit()
        db.refresh(task)
        _normalize_task_datetimes(task)
        return task
    except SQLAlchemyError:
        db.rollback()
        raise


def _normalize_task_datetimes(task: Task) -> None:
    """Ensure datetimes are timezone-aware UTC for API responses.

    SQLite often returns naive datetimes. Add UTC tzinfo when missing.
    """
    if getattr(task, "due_date", None) is not None and task.due_date.tzinfo is None:
        task.due_date = task.due_date.replace(tzinfo=timezone.utc)
    if getattr(task, "created_at", None) is not None and task.created_at.tzinfo is None:
        task.created_at = task.created_at.replace(tzinfo=timezone.utc)
    if getattr(task, "updated_at", None) is not None and task.updated_at.tzinfo is None:
        task.updated_at = task.updated_at.replace(tzinfo=timezone.utc)

def update_task(db: Session, task_id: int, payload: TaskUpdate) -> Task | None:
    task = db.get(Task, task_id)
    if not task:
        return None

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        if key == "title" and isinstance(value, str):
            setattr(task, key, value.strip())
        else:
            setattr(task, key, value)
    task.updated_at = datetime.now(timezone.utc)

    try:
        db.add(task)
        db.commit()
        db.refresh(task)
        _normalize_task_datetimes(task)
        return task
    except SQLAlchemyError:
        db.rollback()
        raise
