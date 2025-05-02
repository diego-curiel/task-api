from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


def datetime_now() -> datetime:
    """
    Returns the actual date and time in UTC
    """
    return datetime.now(timezone.utc)


# Database model for tasks
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # Task title
    title: str
    # Optional task description
    description: Optional[str] = None
    # Is the task completed
    completed: bool = Field(default=False)
    # Creation date
    created_at: datetime = Field(default_factory=datetime_now)


