from sqlalchemy.orm import Session
from app.db.models.task import Task
from sqlalchemy.exc import SQLAlchemyError

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
