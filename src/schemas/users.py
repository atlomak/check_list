import datetime

from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str
    is_superuser: bool
    email: str
    created_at: datetime.datetime

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    username: str
    password: str
    email: str

    class Config:
        orm_mode = True
