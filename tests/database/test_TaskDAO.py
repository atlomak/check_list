import pytest

from src.database._db import Base, SessionLocal, engine
from src.database.tasks_db import TaskDB, TaskDAO
from src.schemas.tasks import Task


@pytest.fixture
def prepared_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    task1 = TaskDB(name="test1", description="test1")
    task2 = TaskDB(name="test2", description="test2", prerequisite_tasks=[task1])
    task3 = TaskDB(name="test3", description="test3", prerequisite_tasks=[task1, task2])
    db.add(task1)
    db.add(task2)
    db.add(task3)
    db.commit()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_get_all_tasks(prepared_db):
    taskdao = TaskDAO(session_factory=SessionLocal)
    tasks: list[Task] = taskdao.get_all_tasks()
    assert len(tasks) == 3
    assert tasks[0].name == "test1"
    assert tasks[1].name == "test2"
    assert tasks[2].name == "test3"


def test_get_task_by_id(prepared_db):
    taskdao = TaskDAO(session_factory=SessionLocal)
    task: Task = taskdao.get_task_by_id(1)
    assert task.name == "test1"
    assert task.description == "test1"
    assert len(task.prerequisite_tasks) == 0

def test_get_task_with_other_tasks_as_prerequisites(prepared_db):
    taskdao = TaskDAO(session_factory=SessionLocal)
    task: Task = taskdao.get_task_by_id(3)
    assert task.name == "test3"
    assert task.description == "test3"
    assert len(task.prerequisite_tasks) == 2
    assert task.prerequisite_tasks[0].name == "test1"
    assert task.prerequisite_tasks[1].name == "test2"
