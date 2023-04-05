from pydantic import BaseModel


class CreateTask(BaseModel):
    name: str
    description: str


class Task(CreateTask):
    id: int
    prerequisite_tasks: list['Task']

    class Config:
        orm_mode = True


CreateTask.update_forward_refs()
