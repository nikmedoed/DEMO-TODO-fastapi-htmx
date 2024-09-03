from sqlalchemy.orm import Session

from .models import Task


def get_tasks(db: Session):
    return db.query(Task).all()


def get_task(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()


def create_task(db: Session, title: str, description: str):
    db_task = Task(title=title, description=description)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
    return task


def update_task_status(db: Session, task_id: int, completed: bool):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.completed = completed
        db.commit()
        db.refresh(task)
    return task
