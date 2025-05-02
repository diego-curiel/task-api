from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlmodel import Field, SQLModel

# Database model for tasks
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # Task title
    title: str
    # Optional task description
    description: Optional[str]
    # Is the task completed
    completed: bool = Field(default=False)
    # Creation date
    created_at: datetime = Field(default_factory=datetime.utcnow)


