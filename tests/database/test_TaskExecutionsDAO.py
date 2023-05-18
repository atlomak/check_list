import pytest
from sqlalchemy.orm import Session

from src.database._db import SessionLocal, Base, engine
from src.database.task_execution_db import TaskExecutionDB, TaskExecutionDAO, TaskAlreadyDone, TaskExecutionNotFound
from src.database.tasks_db import TaskDB
from src.database.user_db import UserDB
from src.schemas.task_executions import CreateTaskExecution


@pytest.fixture
def prepared_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    task1 = TaskDB(name="test1", description="test1")
    task2 = TaskDB(name="test2", description="test2")
    task3 = TaskDB(name="test3", description="test3")
    task4 = TaskDB(id=30, name="test4", description="test3")
    user1 = UserDB(username='test', name="adam", surname="smith", password_hash='test')

    task_execution1 = TaskExecutionDB(task_id=1, user_id=1)
    task_execution2 = TaskExecutionDB(task_id=2, user_id=1)
    task_execution3 = TaskExecutionDB(id=5, task_id=30, user_id=1)

    db.add(task1)
    db.add(task2)
    db.add(task3)
    db.add(task4)
    db.add(user1)
    db.commit()
    db.add(task_execution1)
    db.add(task_execution2)
    db.add(task_execution3)
    db.commit()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_get_task_execution_by_id(prepared_db: Session):
    task_execution_dao = TaskExecutionDAO(session_factory=SessionLocal)
    task_execution = task_execution_dao.get_task_execution_by_id(1)

    assert task_execution.id == 1
    assert task_execution.task_id == 1
    assert task_execution.user_id == 1


def test_get_task_execution_by_id_not_found(prepared_db: Session):
    task_execution_dao = TaskExecutionDAO(session_factory=SessionLocal)
    task_execution = task_execution_dao.get_task_execution_by_id(3)

    assert task_execution is None


def test_get_task_executions_by_user_id(prepared_db: Session):
    task_execution_dao = TaskExecutionDAO(session_factory=SessionLocal)
    task_executions = task_execution_dao.get_task_executions_by_user(1)

    assert len(task_executions) == 3
    assert task_executions[0].id == 1
    assert task_executions[0].task_id == 1


def test_get_all_task_executions(prepared_db: Session):
    task_execution_dao = TaskExecutionDAO(session_factory=SessionLocal)
    task_executions = task_execution_dao.get_all_task_executions()

    assert len(task_executions) == 3
    assert task_executions[0].id == 1
    assert task_executions[0].task_id == 1


def test_add_task_execution(prepared_db: Session):
    task_execution_dao = TaskExecutionDAO(session_factory=SessionLocal)
    task_execution = CreateTaskExecution(user_id=1, task_id=3)

    task_execution_dao.add_task_execution(task_execution)

    task_execution_from_db: TaskExecutionDB = prepared_db.query(TaskExecutionDB).filter(
        TaskExecutionDB.task_id == 3).first()

    assert task_execution_from_db.user_id == 1


def test_add_task_execution_when_task_already_done(prepared_db: Session):
    task_execution_dao = TaskExecutionDAO(session_factory=SessionLocal)
    task_execution = CreateTaskExecution(user_id=1, task_id=1)

    with pytest.raises(TaskAlreadyDone) as e:
        task_execution_dao.add_task_execution(task_execution)

        assert e.value.task_id == 1


def test_delete_task_execution(prepared_db: Session):
    task_execution_dao = TaskExecutionDAO(session_factory=SessionLocal)
    task_execution_dao.delete_task_execution(1)

    task_execution_from_db: TaskExecutionDB = prepared_db.query(TaskExecutionDB).filter(TaskExecutionDB.id == 1).first()

    assert task_execution_from_db is None


def test_delete_task_execution_not_found(prepared_db: Session):
    task_execution_dao = TaskExecutionDAO(session_factory=SessionLocal)
    with pytest.raises(TaskExecutionNotFound) as e:
        task_execution_dao.delete_task_execution(3)
        assert e.value.id == 3


def test_delete_task_execution_by_task_id(prepared_db: Session):
    task_execution_dao = TaskExecutionDAO(session_factory=SessionLocal)
    task_execution_dao.delete_task_execution_by_task_id(30)

    task_execution_from_db: TaskExecutionDB = prepared_db.query(TaskExecutionDB).filter(
        TaskExecutionDB.task_id == 30).first()

    assert task_execution_from_db is None


def test_delete_task_execution_by_task_id_not_found(prepared_db: Session):
    task_execution_dao = TaskExecutionDAO(session_factory=SessionLocal)
    with pytest.raises(TaskExecutionNotFound) as e:
        task_execution_dao.delete_task_execution_by_task_id(5)
        assert e.value.task_id == 5
