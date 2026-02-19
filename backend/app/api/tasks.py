from fastapi import APIRouter, HTTPException, status, Depends, Response
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.models import Task, TaskCreate, TaskUpdate, TaskStatus, Priority
from app.services.task_service import (
    create_task,
    get_task_by_id,
    list_tasks,
    update_task,
    delete_task,
)
from app.api.dependencies import get_current_user
from app.db.database import get_database


router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task_endpoint(
    task: TaskCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Create a new task.

    Validates task data, creates task in database,
    and returns created task with 201 status.
    """
    result = await create_task(task, db)
    return result


@router.get("/{task_id}", response_model=Task)
async def get_task_endpoint(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Get a task by ID.

    Returns task with 200 status, or 404 if not found.
    """
    try:
        result = await get_task_by_id(task_id, db)
        if result:
            return result
        raise HTTPException(status_code=404, detail="Task not found")
    except Exception:
        raise HTTPException(status_code=404, detail="Invalid task ID format")


@router.get("", response_model=List[Task])
async def list_tasks_endpoint(
    list_id: str,
    status: Optional[TaskStatus] = None,
    priority: Optional[Priority] = None,
    sort: Optional[str] = None,
    skip: Optional[int] = None,
    limit: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    List tasks for a given list_id with optional filtering and sorting.

    Returns list of tasks with 200 status.
    """
    result = await list_tasks(
        list_id=list_id,
        status=status,
        priority=priority,
        sort=sort,
        skip=skip,
        limit=limit,
        db=db,
    )
    return result


@router.put("/{task_id}", response_model=Task)
async def update_task_endpoint(
    task_id: str,
    task_update: TaskUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Update an existing task.

    Validates task exists, updates fields in database,
    and returns updated task with 200 status, or 404 if not found.
    """
    try:
        result = await update_task(task_id, task_update, db)
        if result:
            return result
        raise HTTPException(status_code=404, detail="Task not found")
    except Exception:
        raise HTTPException(status_code=404, detail="Invalid task ID format")


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_endpoint(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Delete a task by ID.

    Deletes task from database, returns 204 status.
    Returns 404 if task not found.
    """
    success = await delete_task(task_id, db)

    if success:
        return Response(status_code=204)
    else:
        raise HTTPException(status_code=404, detail="Task not found")
