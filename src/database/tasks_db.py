from typing import Annotated

from fastapi import Depends
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship, sessionmaker

from ._db import Base, get_session_factory
from ..schemas.tasks import Task, CreateTask

task_prerequisites = Table(
    "task_prerequisites",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id"), primary_key=True),
    Column("prerequisite_id", Integer, ForeignKey("tasks.id"), primary_key=True),
)


class TaskDB(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(50), nullable=True)
    prerequisite_tasks = relationship(
        "TaskDB",
        secondary=task_prerequisites,
        primaryjoin=(task_prerequisites.c.task_id == id),
        secondaryjoin=(task_prerequisites.c.prerequisite_id == id),
        backref="tasks",
    )

    def __repr__(self):
        return f'Task {self.name}'


class TaskDAO:
    def __init__(self, session_factory: Annotated[sessionmaker, Depends(get_session_factory)]):
        self.Session = session_factory

    def get_task_by_id(self, id: int) -> Task | None:
        with self.Session() as session:
            taskdb = session.query(TaskDB).get(id)
            if not taskdb:
                return None
            task = Task.from_orm(taskdb)
        return task

    def get_task_by_name(self, name: str) -> Task | None:
        with self.Session() as session:
            taskdb = session.query(TaskDB).filter(TaskDB.name == name).first()
            if not taskdb:
                return None
            task = Task.from_orm(taskdb)
        return task

    def get_all_tasks(self) -> list[Task]:
        with self.Session() as session:
            tasks = session.query(TaskDB).all()
            return [Task.from_orm(task) for task in tasks]

    def get_tasks_by_prerequisite(self, id: int) -> list[Task] | None:
        with self.Session() as session:
            tasks = session.query(TaskDB).filter(TaskDB.prerequisite_tasks.any(id=id)).all()
            return [Task.from_orm(task) for task in tasks]

    def add_task(self, task: CreateTask):
        try:
            with self.Session() as session, session.begin():
                taskdb = TaskDB(name=task.name, description=task.description)
                session.add(taskdb)
                session.commit()
        except IntegrityError as e:
            raise TaskAlreadyExists(task_name=task.name) from e

    def modify_task(self,id: int, *args, **kwargs):
        with self.Session() as session, session.begin():
            taskdb = session.query(TaskDB).get(id)
            if not taskdb:
                raise TaskNotFound(id)
            for key, value in kwargs.items():
                if hasattr(taskdb, key):
                    if key == "prerequisite_tasks":
                        taskdb.prerequisite_tasks = []
                        for prerequisite_task in value:
                            taskdb.prerequisite_tasks.append(session.query(TaskDB).get(prerequisite_task.id))
                    else:
                        setattr(taskdb, key, value)
                else:
                    raise AttributeError(f"TaskDB has no attribute {key}")
            session.commit()

class TaskAlreadyExists(Exception):
    def __init__(self, task_name):
        self.task_name = task_name
        super().__init__(f"Task with name {task_name} already exists")

class TaskNotFound(Exception):
    def __init__(self, id):
        self.id = id
        super().__init__(f"Task with id {id} not found")