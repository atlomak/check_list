import pytest

from src.database._db import SessionLocal, Base, engine
from src.database.user_db import UserDAO, UserDB, UserAlreadyExists
from src.schemas.users import User, SafeUserCreate


@pytest.fixture
def prepared_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    db_user = UserDB(username='test', name="adam", surname="smith", password_hash='test')
    db_user2 = UserDB(username='test2', name="john", surname="smith", password_hash='test')
    db_user3 = UserDB(username='test3', name="chris", surname="smith", password_hash='test')
    db.add(db_user)
    db.add(db_user2)
    db.add(db_user3)
    db.commit()
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
    assert user.name == 'adam'
    assert user.surname == 'smith'


def test_get_user_by_id_not_found(prepared_db):
    userdao = UserDAO(session_factory=SessionLocal)
    user: User = userdao.get_user_by_id(4)

    assert user is None


def test_get_user_by_username(prepared_db):
    userdao = UserDAO(session_factory=SessionLocal)
    user: User = userdao.get_user_by_username("test")

    assert user.id == 1
    assert user.username == "test"
    assert user.name == "adam"
    assert user.surname == "smith"


def test_get_user_by_username_not_found(prepared_db):
    userdao = UserDAO(session_factory=SessionLocal)
    user: User = userdao.get_user_by_username("not_test_name")

    assert user is None


def test_get_all_users(prepared_db):
    userdao = UserDAO(session_factory=SessionLocal)
    users: list[User] = userdao.get_all_users()
    assert len(users) == 3
    assert users[0].id == 1
    assert users[0].username == "test"
    assert users[0].name == "adam"


def test_add_user(prepared_db):
    userdao = UserDAO(session_factory=SessionLocal)
    user = SafeUserCreate(username='test4', name="adam", surname="Kowalski", password_hash='test')
    userdao.add_user(user)

    user_from_db = prepared_db.query(UserDB).filter(UserDB.username == 'test4').first()

    assert user.username == user_from_db.username
    assert 4 == user_from_db.id


def test_add_user_already_in_db(prepared_db):
    userdao = UserDAO(session_factory=SessionLocal)
    user = SafeUserCreate(username='test', name="adam", surname="Kowalski", password_hash='test')
    with pytest.raises(UserAlreadyExists) as e:
        userdao.add_user(user)
        assert e.value.message == "'User with username test already exists'"
        assert e.value.username == "test"


def test_modify_user_name(prepared_db):
    userdao = UserDAO(session_factory=SessionLocal)
    userdao.modify_user(1, name="new_name")

    user_from_db = prepared_db.query(UserDB).filter(UserDB.id == 1).first()

    assert user_from_db.name == "new_name"


def test_modify_user_surname(prepared_db):
    userdao = UserDAO(session_factory=SessionLocal)
    userdao.modify_user(1, surname="new_surname")

    user_from_db = prepared_db.query(UserDB).filter(UserDB.id == 1).first()

    assert user_from_db.surname == "new_surname"


def test_modify_wrong_parameter(prepared_db):
    userdao = UserDAO(session_factory=SessionLocal)
    with pytest.raises(AttributeError) as e:
        userdao.modify_user(id=1, wrong_parameter="new_surname")
        assert e.value.message == "AttributeError: 'UserDAO' object has no attribute wrong_parameter"


def test_delete_user(prepared_db):
    userdao = UserDAO(session_factory=SessionLocal)
    userdao.delete_user(id=1)

    user_from_db = prepared_db.query(UserDB).filter(UserDB.id == 1).first()

    assert user_from_db is None
