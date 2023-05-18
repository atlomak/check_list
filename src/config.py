from pydantic import BaseSettings


class Settings(BaseSettings):
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_name: str = "postgres"
    db_host: str = "postgres"
    db_port: int = 5432


settings = Settings()
