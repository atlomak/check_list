import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    name: str
    surname: str


class User(UserBase):
    id: int
    is_superuser: bool
    created_at: datetime.datetime

    class Config:
        orm_mode = True


class UserInDB(User):
    password_hash: str


class UserCreate(UserBase):
    password: str


class SafeUserCreate(UserBase):
    password_hash: str
