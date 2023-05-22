import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from src.database._db import get_session_factory, Base
from src.schemas.task_executions import TaskExecution, CreateTaskExecution


class TaskExecutionDB(Base):
    __tablename__ = 'task_executions'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    execution_date = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'TaskExecution {self.id}'


class TaskExecutionDAO:
    def __init__(self, session_factory: Annotated[sessionmaker, Depends(get_session_factory)]):
        self.Session = session_factory

    def get_task_execution_by_id(self, id: int) -> TaskExecution | None:
        with self.Session() as session:
            task_execution = session.get(TaskExecutionDB,id)
            if task_execution is None:
                return None
            task_execution = TaskExecution.from_orm(task_execution)
        return task_execution

    def get_task_executions_by_user(self, user_id: int) -> list[TaskExecution]:
        with self.Session() as session:
            tasks_execution = session.query(TaskExecutionDB).filter(TaskExecutionDB.user_id == user_id).all()
            return [TaskExecution.from_orm(task_execution) for task_execution in tasks_execution]

    def get_all_task_executions(self):
        with self.Session() as session:
            task_executions = session.query(TaskExecutionDB).all()
            return [TaskExecution.from_orm(task_execution) for task_execution in task_executions]

    def add_task_execution(self, task_execution: CreateTaskExecution):
        try:
            with self.Session() as session, session.begin():
                task_execution_db = TaskExecutionDB(user_id=task_execution.user_id, task_id=task_execution.task_id)
                session.add(task_execution_db)
                session.commit()
        except IntegrityError as e:
            raise TaskAlreadyDone(task_execution.task_id) from e

    def delete_task_execution(self, id: int):
        with self.Session() as session, session.begin():
            task_execution = session.get(TaskExecutionDB,id)
            if task_execution is None:
                raise TaskExecutionNotFound(id)
            session.delete(task_execution)
            session.commit()

    def delete_task_execution_by_task_id(self, task_id: int):
        with self.Session() as session, session.begin():
            task_execution = session.query(TaskExecutionDB).filter(TaskExecutionDB.task_id == task_id).first()
            if task_execution is None:
                raise TaskExecutionNotFound(task_id)
            session.delete(task_execution)
            session.commit()


class TaskAlreadyDone(Exception):
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task with id {task_id} is already in task_executions table")


class TaskExecutionNotFound(Exception):
    def __init__(self, id: int = None, task_id: int = None):
        self.id = id
        self.task_id = task_id
        super().__init__(f"Task execution with id {id} and task_id {task_id} not found")
