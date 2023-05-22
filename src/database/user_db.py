import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from src.schemas.users import UserInDB, SafeUserCreate
from ._db import Base, get_session_factory


class UserDB(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    password_hash = Column(String(128), nullable=False)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'User {self.username}'


class UserDAO:
    def __init__(self, session_factory: Annotated[sessionmaker, Depends(get_session_factory)]):
        self.Session = session_factory

    def get_user_by_id(self, id: int) -> UserInDB | None:
        with self.Session() as session:
            userdb: UserDB = session.query(UserDB).filter(UserDB.id == id).first()
            if userdb is None:
                return None
            user = UserInDB.from_orm(userdb)
            return user

    def get_user_by_username(self, username: str) -> UserInDB | None:
        with self.Session() as session:
            userdb: UserDB = session.query(UserDB).filter(UserDB.username == username).first()
            if userdb is None:
                return None
            user = UserInDB.from_orm(userdb)
            return user

    def get_all_users(self) -> list[UserInDB]:
        with self.Session() as session:
            users = session.query(UserDB).all()
            return [UserInDB.from_orm(user) for user in users]

    def add_user(self, user: SafeUserCreate):
        try:
            with self.Session() as session, session.begin():
                userdb = UserDB(username=user.username, name=user.name, surname=user.surname,
                                password_hash=user.password_hash)
                session.add(userdb)
                session.commit()
        except IntegrityError as e:
            raise UserAlreadyExists(user.username) from e

    def modify_user(self, id: int, *args, **kwargs):
        with self.Session() as session, session.begin():
            userdb: UserDB = session.query(UserDB).filter(UserDB.id == id).first()
            if userdb is None:
                raise UserNotFound(id)
            for key, value in kwargs.items():
                if hasattr(userdb, key):
                    setattr(userdb, key, value)
                else:
                    raise AttributeError(f'UserDB has no attribute {key}')
            session.commit()

    def delete_user(self, id: int):
        with self.Session() as session, session.begin():
            userdb: UserDB = session.query(UserDB).filter(UserDB.id == id).first()
            if userdb is None:
                raise UserNotFound(id)
            session.delete(userdb)
            session.commit()


class UserAlreadyExists(Exception):
    def __int__(self, username: str):
        self.username = username
        super().__init__(f'User with username {username} already exists')


class UserNotFound(Exception):
    def __int__(self, id: int):
        self.id = id
        super().__init__(f'User with id {id} not found')
