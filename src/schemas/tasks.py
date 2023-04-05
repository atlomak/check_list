from pydantic import BaseModel


class Task(BaseModel):
    id: int
    name: str
    description: str
    prerequisite_tasks: list['Task']

    class Config:
        orm_mode = True


class CreateTask(BaseModel):
    name: str
    description: str


Task.update_forward_refs()
