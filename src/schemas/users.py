import datetime

from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str
    name: str
    surname: str
    is_superuser: bool
    created_at: datetime.datetime

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    username: str
    name: str
    surname: str
    password: str

    class Config:
        orm_mode = True
