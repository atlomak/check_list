from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship

from ._db import Base
from ..schemas.tasks import Task

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
    def __init__(self, session_factory):
        self.Session = session_factory

    def get_task_by_id(self, id: int) -> Task | None:
        with self.Session() as session:
            taskdb = session.query(TaskDB).get(id)
            if not taskdb:
                return None
            task = Task.from_orm(taskdb)
        return task

    def get_all_tasks(self) -> list[Task]:
        with self.Session() as session:
            tasks = session.query(TaskDB).all()
            return [Task.from_orm(task) for task in tasks]

