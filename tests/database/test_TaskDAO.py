import pytest
from sqlalchemy.orm import Session

from src.database._db import Base, SessionLocal, engine
from src.database.tasks_db import TaskDB, TaskDAO, TaskAlreadyExists
from src.schemas.tasks import Task, CreateTask


@pytest.fixture
def prepared_db() -> Session:
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


def test_get_task_by_id_not_found(prepared_db):
    taskdao = TaskDAO(session_factory=SessionLocal)
    task: Task = taskdao.get_task_by_id(4)
    assert task is None


def test_get_task_by_name(prepared_db):
    taskdao = TaskDAO(session_factory=SessionLocal)
    task: Task = taskdao.get_task_by_name("test1")
    assert task.name == "test1"
    assert task.description == "test1"
    assert len(task.prerequisite_tasks) == 0


def test_get_task_by_name_not_found(prepared_db):
    taskdao = TaskDAO(session_factory=SessionLocal)
    task: Task = taskdao.get_task_by_name("not_test_name")
    assert task is None


def test_get_tasks_by_prerequisite(prepared_db):
    taskdao = TaskDAO(session_factory=SessionLocal)
    tasks: list[Task] = taskdao.get_tasks_by_prerequisite(1)
    assert len(tasks) == 2
    assert tasks[0].name == "test2"
    assert tasks[1].name == "test3"


def test_get_tasks_by_prerequisite_not_found(prepared_db):
    taskdao = TaskDAO(session_factory=SessionLocal)
    tasks: list[Task] = taskdao.get_tasks_by_prerequisite(4)
    assert len(tasks) == 0


def test_get_tasks_by_prerequisite_with_other_tasks_as_prerequisites(prepared_db):
    taskdao = TaskDAO(session_factory=SessionLocal)
    tasks: list[Task] = taskdao.get_tasks_by_prerequisite(2)
    assert len(tasks) == 1
    assert tasks[0].name == "test3"
    assert len(tasks[0].prerequisite_tasks) == 2
    assert tasks[0].prerequisite_tasks[0].name == "test1"
    assert tasks[0].prerequisite_tasks[1].name == "test2"


def test_add_task(prepared_db: Session):
    taskdao = TaskDAO(session_factory=SessionLocal)
    task = CreateTask(name="test_task5",
                      description="test_desc")

    taskdao.add_task(task)

    task_from_db = prepared_db.query(TaskDB).filter(TaskDB.name == "test_task5").first()

    assert task_from_db.name == "test_task5"
    assert task_from_db.description == "test_desc"
    assert len(task_from_db.prerequisite_tasks) == 0


def test_add_task_already_in_db(prepared_db):
    taskdao = TaskDAO(session_factory=SessionLocal)
    task = CreateTask(name="test1", description="test1")
    with pytest.raises(TaskAlreadyExists) as e:
        taskdao.add_task(task)
        assert e.value.task_name == "test1"


def test_task_modify_add_existing_prerequisites(prepared_db):
    taskdao = TaskDAO(session_factory=SessionLocal)
    task = Task(id=1, name="test1", description="test1", prerequisite_tasks=[])

    taskdao.modify_task(2, prerequisite_tasks=[task])

    task_from_db = prepared_db.get(TaskDB, 2)

    assert task_from_db.name == "test2"
    assert task_from_db.description == "test2"
    assert len(task_from_db.prerequisite_tasks) == 1
    assert task_from_db.prerequisite_tasks[0].name == "test1"
