import pytest
from sqlalchemy.orm import Session

from src.database._db import Base, SessionLocal, engine
from src.database.tag_db import TagDB, TagDAO, TagAlreadyExists
from src.schemas.tags import CreateTag


@pytest.fixture
def prepared_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    tag1 = TagDB(name="Mechanics")
    tag2 = TagDB(name="Electronics")
    tag3 = TagDB(name="Safety")
    db.add(tag1)
    db.add(tag2)
    db.add(tag3)
    db.commit()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_add_tag(prepared_db: Session):
    tagdao = TagDAO(session_factory=SessionLocal)
    tag = CreateTag(name="TestTag")

    tagdao.add_tag(tag)

    tag_from_db = prepared_db.query(TagDB).filter(TagDB.name == "TestTag").first()

    assert tag_from_db.name == "TestTag"
    assert tag_from_db.id == 4


def test_add_tag_already_exists(prepared_db: Session):
    tagdao = TagDAO(session_factory=SessionLocal)
    tag = CreateTag(name="Mechanics")

    with pytest.raises(TagAlreadyExists) as e:
        tagdao.add_tag(tag)
        assert e.value.tag_name == "Mechanics"


def test_get_tag_by_id(prepared_db: Session):
    tagdao = TagDAO(session_factory=SessionLocal)
    tag = tagdao.get_tag_by_id(1)
    assert tag.name == "Mechanics"
    assert tag.id == 1


def test_get_tag_by_id_not_found(prepared_db: Session):
    tagdao = TagDAO(session_factory=SessionLocal)
    tag = tagdao.get_tag_by_id(4)
    assert tag is None


def test_get_tag_by_name(prepared_db: Session):
    tagdao = TagDAO(session_factory=SessionLocal)
    tag = tagdao.get_tag_by_name("Mechanics")
    assert tag.name == "Mechanics"
    assert tag.id == 1


def test_get_tag_by_name_not_found(prepared_db: Session):
    tagdao = TagDAO(session_factory=SessionLocal)
    tag = tagdao.get_tag_by_name("TestTag")
    assert tag is None


def test_get_all_tags(prepared_db: Session):
    tagdao = TagDAO(session_factory=SessionLocal)
    tags = tagdao.get_all_tags()
    assert len(tags) == 3
    assert tags[0].name == "Mechanics"
    assert tags[0].id == 1
    assert tags[1].name == "Electronics"
    assert tags[1].id == 2
    assert tags[2].name == "Safety"
    assert tags[2].id == 3


def test_delete_tag(prepared_db: Session):
    tagdao = TagDAO(session_factory=SessionLocal)
    tagdao.delete_tag(1)

    tag_from_db = prepared_db.get(TagDB, 1)
    assert tag_from_db is None
