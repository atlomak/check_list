import pytest
from sqlalchemy.exc import IntegrityError

from src.database._db import SessionLocal, Base
from src.database.user_db import UserDB


@pytest.fixture
def db():
    db = SessionLocal()
    Base.metadata.create_all(bind=db.bind)
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=db.bind)


# Sanity check of sqlalchemy

def test_add_user(db):
    user = UserDB(username='test',name="Julia", surname="test", password_hash='test')

    db.add(user)
    db.commit()

    user_from_db = db.query(UserDB).filter(UserDB.username == 'test').first()

    assert 1 == user_from_db.id
    assert "test" == user_from_db.username


def test_add_user_with_same_username(db):
    user = UserDB(username='test',name="Julia", surname="test", password_hash='test')
    user2 = UserDB(username='test',name="Julia", surname="test", password_hash='test')

    with pytest.raises(IntegrityError):
        db.add(user)
        db.add(user2)
        db.commit()


def test_modifying_user(db):
    user = UserDB(username='test',name="Julia", surname="test", password_hash='test')

    db.add(user)
    db.commit()
    db.close()

    user = db.query(UserDB).filter(UserDB.username == 'test').first()
    user.username = 'test2'

    db.add(user)
    db.commit()
    db.close()

    user_after_modification = db.query(UserDB).filter(UserDB.id == 1).first()

    assert len(db.query(UserDB).all()) == 1
    assert user_after_modification.username == 'test2'
