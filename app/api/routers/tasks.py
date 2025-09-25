from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api import deps
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.schemas.error import ErrorResponse
from app.services import tasks as task_service

router = APIRouter(tags=["tasks"])

# ---------------------------
# GET /v1/tasks
# ---------------------------
@router.get("/", response_model=List[TaskRead])
def list_tasks(
    task_id: Optional[int] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    db: Session = Depends(deps.get_db),
):
    return task_service.list_tasks(db, task_id=task_id, status=status, priority=priority)


# ---------------------------
# POST /v1/tasks
# ---------------------------
@router.post(
    "/",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def create_task(task: TaskCreate, db: Session = Depends(deps.get_db)):
    return task_service.create_task(db, task)


# ---------------------------
# PATCH /v1/tasks/{task_id}
# ---------------------------
@router.patch(
    "/{task_id}",
    response_model=TaskRead,
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(deps.get_db)):
    updated = task_service.update_task(db, task_id, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return updated


# ---------------------------
# DELETE /v1/tasks/{task_id}
# ---------------------------
@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}}
)
def delete_task(task_id: int, db: Session = Depends(deps.get_db)):
    success = task_service.delete_task(db, task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
