from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_name: str = "postgres"
    db_host: str = "postgres"
    db_port: int = 5432


class SecuritySetting(BaseSettings):
    jwt_secret: str
