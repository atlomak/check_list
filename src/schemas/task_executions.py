import datetime

from pydantic import BaseModel


class CreateTaskExecution(BaseModel):
    task_id: int
    user_id: int


class TaskExecution(CreateTaskExecution):
    id: int
    execution_date: datetime.datetime

    class Config:
        orm_mode = True
