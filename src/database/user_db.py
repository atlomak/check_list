import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker

from src.schemas.users import User, UserCreate
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

    def get_user_by_id(self, id: int) -> User | None:
        with self.Session() as session:
            userdb: UserDB = session.query(UserDB).filter(UserDB.id == id).first()
            if userdb is None:
                return None
            user = User.from_orm(userdb)
            return user

    def get_user_by_username(self, username: str) -> User | None:
        with self.Session() as session:
            userdb: UserDB = session.query(UserDB).filter(UserDB.username == username).first()
            if userdb is None:
                return None
            user = User.from_orm(userdb)
            return user

    def add_user(self, user: UserCreate):
        with self.Session() as session, session.begin():
            userdb = UserDB(username=user.username, name=user.name, surname=user.surname, password_hash=user.password)
            session.add(userdb)
            session.commit()
