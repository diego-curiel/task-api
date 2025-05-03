from datetime import datetime
from typing import Optional

import pydantic as pyd
from sqlmodel import Field, SQLModel

from utils import datetime_now


# Base task model
class BaseTask(SQLModel):
    # Task title
    title: str = Field(max_length=120)
    # Optional task description
    description: Optional[str] = Field(default=None, nullable=True, 
                                       max_length=255)
    # Whether the task was completed
    completed: bool = Field(default=False)
    # Creation date
    created_at: datetime = Field(default_factory=datetime_now)


# Database model for tasks
class Task(BaseTask, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


# Model used to create and update (PUT) new tasks
class TaskCreate(BaseTask):
    pass # Just in case something changes in the future


# Model used to show tasks to the users
class TaskPublic(BaseTask):
    id: int


# Model used to handle task patches
class TaskPatch(pyd.BaseModel):
    # Make the title optional since this is a patch model
    title: Optional[str] = pyd.Field(default=None,max_length=120)
    # The task description was optional since the beginning
    description: Optional[str] = pyd.Field(default=None, max_length=255)
    # This was also optional since the default value was False
    completed: bool = pyd.Field(default=False)
    # The creation date must default to None in order to not change anything
    created_at: Optional[datetime] = pyd.Field(default=None)

