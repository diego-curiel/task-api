from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, Query, status
from sqlmodel import col, select

from models import Task, TaskCreate, TaskPatch, TaskPublic
from dependencies import DatabaseDep


task_router = APIRouter(prefix="/task", tags=["tasks"])

@task_router.get("/", response_model=list[TaskPublic])
def list_tasks(
    db_session: DatabaseDep,
    offset: Annotated[int, Query(ge=0)]=0,
    limit: Annotated[int, Query(ge=0)]=20,
    title: Annotated[str, Query(max_length=120)] = "",
):
    """
    Retrieve a list of tasks from the database with optional filtering and pagination.

    Parameters:
        db_session (DatabaseDep): Dependency-injected database session.
        offset (int, optional): Number of items to skip before starting to collect the result set. Must be >= 0. Default is 0.
        limit (int, optional): Maximum number of items to return. Must be >= 0. Default is 20.
        title (str, optional): Optional title filter. Returns tasks whose titles contain this string (case-insensitive). Max length is 120 characters.

    Returns:
        list[Task]: A list of Task objects matching the criteria.

    Raises:
        HTTPException: If no tasks are found matching the criteria, raises a 404 NOT FOUND.
    """
    # Select statement
    statement = select(Task).offset(offset).limit(limit)
    
    # Filter the tasks by title
    if title:
        statement = statement.where(col(Task.title).ilike(f"%{title}%"))

    # Get all the tasks 
    task_list = db_session.exec(statement).all()

    # Raise an HTTP status 404 NOT FOUND if the list is empty
    if not task_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="The tasks list is empty.") 
    

    return list(task_list)


@task_router.post("/", response_model=TaskPublic, status_code=201)
def create_task(
    db_session: DatabaseDep,
    task: Annotated[TaskCreate, Body()],
):
    """
    Create a new task in the database.

    Parameters:
        db_session (DatabaseDep): Dependency-injected database session.
        task (TaskCreate): Task body object of the HTTP request.

    Returns:
        TaskPublic: The Task object created.
    """
    # Validate the input data with the database model
    db_task = Task.model_validate(task)
    # Add the object to the database
    db_session.add(db_task)
    db_session.commit()
    # Refresh the object by retrieving data from the database
    db_session.refresh(db_task)

    return db_task

