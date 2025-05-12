from typing import Annotated

from fastapi import (
    APIRouter, 
    Body, 
    HTTPException, 
    Path, 
    Query, 
    status
)
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


@task_router.get("/{task_id}", response_model=TaskPublic)
def task_details(
    db_session: DatabaseDep,
    task_id: Annotated[int, Path(ge=0)],
) -> Task:
    """
    Retrieve a task from the database and return its details.

    Parameters:
        db_session (DatabaseDep): Dependency-injected database session.
        task_id: ID of the task to be detailed.

    Returns:
        Task: Details of the Task object retrieved by its ID.

    Raises:
        HTTPException: If the task with the given ID does not exist, raises a 404 NOT FOUND.
    """
    # Retrieve the task from the database
    task_db = db_session.get(Task, task_id)
    # Raise an HTTPException if the task with the given ID does not exist
    if not task_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Task not found")
    return task_db


@task_router.post("/", response_model=TaskPublic, status_code=201)
def create_task(
    db_session: DatabaseDep,
    task_body: Annotated[TaskCreate, Body()],
):
    """
    Create a new task in the database.

    Parameters:
        db_session (DatabaseDep): Dependency-injected database session.
        task_body (TaskCreate): Task body object of the HTTP request.

    Returns:
        TaskPublic: The Task object created.
    """
    # Validate the input data with the database model
    db_task = Task.model_validate(task_body)
    # Add the object to the database
    db_session.add(db_task)
    db_session.commit()
    # Refresh the object by retrieving data from the database
    db_session.refresh(db_task)

    return db_task


@task_router.put("/{task_id}", response_model=TaskPublic)
def update_task(
    db_session: DatabaseDep,
    task_id: Annotated[int, Path(ge=1)],
    task_body: Annotated[TaskCreate, Body()],
) -> Task:
    """
    Update an existing task by ID with new data.

    This endpoint retrieves a task by its ID from the database, updates its fields
    with the values provided in the request body, and commits the changes.

    Parameters:
        db_session (DatabaseDep): Dependency-injected database session.
        task_id (int): ID of the task to retrieve from the database.
        task_body (TaskCreate): The new task data. Fields not included will be left unchanged.

    Returns:
        Task: The updated task object.

    Raises:
        HTTPException: If the task with the given ID does not exist, raises a 404 NOT FOUND.
    """
    # Look for the task to update in the database
    task_db = db_session.get(Task, task_id)
    if not task_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Task not found")
    # The TaskCreate model also works for PUT methods
    task_data = task_body.model_dump(exclude_unset=True)
    # Add the new data to the database model
    task_db.sqlmodel_update(task_data)
    db_session.add(task_db)
    # Save changes and return the object to the client
    db_session.commit()
    db_session.refresh(task_db)

    return task_db


@task_router.patch("/{task_id}", response_model=TaskPublic)
def patch_task(
    db_session: DatabaseDep,
    task_id: Annotated[int, Path(ge=0)],
    task_body: Annotated[TaskPatch, Body()],
):
    """
    Retrieve a task from the database, then update some fields with new data.
    
    This endpoint retrieves a task from the database by its ID, updates some 
    fields with the data provided in the request body and commits the changes.

    Parameters:
        db_session (DatabaseDep): Dependency-injected database session.
        task_id int: ID of the task to retrieve from the database.
        task_body TaskPatch: New data used to update the task model.

    Returns:
        Task: The updated task model.

    Raises:
        HTTPException: If the task with the given ID was not found, raises a 404 NOT FOUND
    """
    task_db = db_session.get(Task, task_id)
    if not task_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Task not found")
    task_data = task_body.model_dump(exclude_unset=True)
    task_db.sqlmodel_update(task_data)
    db_session.add(task_db)
    db_session.commit()
    db_session.refresh(task_db)

    return task_db


@task_router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    db_session: DatabaseDep,
    task_id: Annotated[int, Path()],
):
    """
    Delete a task from the database.

    This endpoint deletes a task with the given ID from the database.

    Parameters:
        db_session (DatabaseDep): Dependency-injected database session.
        task_id (int): ID of the task to be deleted:

    returns:
        dict: A confirmation message with {"ok": True} upon successful deletion.
    """
    task_db = db_session.get(Task, task_id)
    if not task_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Task not found")
    db_session.delete(task_db)
    db_session.commit()

    return {"ok": True}
