from typing import Annotated

from fastapi import Depends
from sqlmodel import Session
from database import engine

def get_database_session():
    """
        Yields a session object to interact with the database.
    """
    with Session(engine) as session:
        yield session

# Session dependency type
DatabaseDep = Annotated[Session, Depends(get_database_session)]
