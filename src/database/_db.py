from sqlalchemy import create_engine, URL
from sqlalchemy.orm import declarative_base, sessionmaker
from src.config import get_settings

Base = declarative_base()

settings = get_settings()

_db_url = URL.create(
    "postgresql",
    username=settings.db_user,
    password=settings.db_password,
    host=settings.db_host,
    database=settings.db_name,
    port=settings.db_port
)

engine = create_engine(_db_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session_factory():
    return SessionLocal
