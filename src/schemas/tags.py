from pydantic import BaseModel


class CreateTag(BaseModel):
    name: str


class Tag(CreateTag):
    id: int

    class Config:
        orm_mode = True
