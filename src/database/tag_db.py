from typing import Annotated

from fastapi import Depends
from sqlalchemy import Column, Integer, String
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from src.schemas.tags import CreateTag, Tag
from ._db import Base, get_session_factory


class TagDB(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True)

    def __repr__(self):
        return f'User {self.name}'


class TagDAO:
    def __init__(self, session_factory: Annotated[sessionmaker, Depends(get_session_factory)]):
        self.Session = session_factory

    def get_tag_by_id(self, id: int) -> Tag | None:
        with self.Session() as session:
            tagdb: TagDB | None = session.get(TagDB, id)
        if tagdb is None:
            return None
        tag = Tag.from_orm(tagdb)
        return tag

    def get_tag_by_name(self, name: str) -> Tag | None:
        with self.Session() as session:
            tagdb = session.query(TagDB).filter(TagDB.name == name).first()
        if not tagdb:
            return None
        tag = Tag.from_orm(tagdb)
        return tag

    def get_all_tags(self) -> list[Tag]:
        with self.Session() as session:
            tags = session.query(TagDB).all()
        return [Tag.from_orm(tag) for tag in tags]

    def add_tag(self, tag: CreateTag):
        try:
            with self.Session() as session, session.begin():
                tagdb = TagDB(name=tag.name)
                session.add(tagdb)
                session.commit()
        except IntegrityError as e:
            raise TagAlreadyExists(tag.name) from e

    def delete_tag(self, id: int):
        with self.Session() as session, session.begin():
            tagdb: TagDB = session.get(TagDB,id)
            if not tagdb:
                raise TagNotFound(id)
            session.delete(tagdb)
            session.commit()


class TagAlreadyExists(Exception):
    def __init__(self, tag_name: str):
        self.tag_name = tag_name
        super().__init__(f"Tag with name {tag_name} already exists")


class TagNotFound(Exception):
    def __init__(self, id: int):
        self.id = id
        super().__init__(f"Tag with id {id} not found")
