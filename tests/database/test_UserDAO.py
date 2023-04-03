import pytest
from sqlalchemy.orm import Session

from src.database._db import SessionLocal, Base, engine
from src.database.user_db import UserDAO, UserDB
from src.schemas.users import User, UserCreate

db_user = UserDB(username='test', password_hash='test', email="test1@test.com")
db_user2 = UserDB(username='test2', password_hash='test', email="test2@test.com")
db_user3 = UserDB(username='test3', password_hash='test', email="test3@test.com")


@pytest.fixture
def prepared_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    db.add(db_user)
    db.add(db_user2)
    db.add(db_user3)
    db.commit()
    db.close()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_get_user_by_id(prepared_db):
    userdao = UserDAO(session_factory=SessionLocal)
    user: User = userdao.get_user_by_id(1)

    assert user.id == 1
    assert user.username == 'test'
    assert user.email == "test1@test.com"


def test_add_user(prepared_db):
    userdao = UserDAO(session_factory=SessionLocal)
    user = UserCreate(username='test4', password='test', email="test4@test.com")
    userdao.add_user(user)

    user_from_db = prepared_db.query(UserDB).filter(UserDB.username == 'test4').first()

    assert user.username == user_from_db.username
    assert user.email == user_from_db.email
    assert 1 == user_from_db.id