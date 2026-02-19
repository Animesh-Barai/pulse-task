from typing import Optional, List, Union
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.models import Task, TaskCreate, TaskUpdate, TaskStatus
from bson.objectid import ObjectId


class InvalidTransitionError(Exception):
    """Raised when attempting an invalid task status transition."""

    pass


async def create_task(task_data: TaskCreate, db: AsyncIOMotorDatabase) -> Task:
    """
    Create a new task in the database.

    Validates task_data using Pydantic model, inserts into MongoDB,
    and returns Task object with all fields populated including timestamps.

    Args:
        task_data: TaskCreate model with task data (title, list_id required)
        db: AsyncIOMotorDatabase instance for MongoDB operations

    Returns:
        Task model with id, all fields from task_data, and timestamps
    """
    # Build task document for MongoDB insertion
    # TaskCreate provides validation and default values (priority=MEDIUM, status=OPEN)
    task_dict = {
        "title": task_data.title,
        "description": task_data.description,
        "priority": task_data.priority,
        "status": task_data.status,
        "due_date": task_data.due_date,
        "tags": task_data.tags,
        "list_id": task_data.list_id,
        "assignee_id": task_data.assignee_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    # Insert into database
    result = await db.tasks.insert_one(task_dict)

    # Return Task model with inserted_id as string
    return Task(
        id=str(result.inserted_id),
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        status=task_data.status,
        due_date=task_data.due_date,
        tags=task_data.tags,
        list_id=task_data.list_id,
        assignee_id=task_data.assignee_id,
        created_at=task_dict["created_at"],
        updated_at=task_dict["updated_at"],
    )


async def get_task_by_id(task_id: str, db: AsyncIOMotorDatabase) -> Optional[Task]:
    """
    Get a task by ID.
    Returns Task model if found, None otherwise.
    """
    try:
        task_dict = await db.tasks.find_one({"_id": ObjectId(task_id)})
        if task_dict:
            task_dict["id"] = str(task_dict["_id"])
            return Task(**task_dict)
    except Exception:
        pass
    return None


async def update_task(
    task_id: str, update_data: TaskUpdate, db: AsyncIOMotorDatabase
) -> Optional[Task]:
    """
    Update an existing task with provided fields.

    Validates task exists, updates with non-None fields from update_data,
    sets updated_at timestamp, and returns updated Task object.

    Args:
        task_id: The ID of the task to update
        update_data: TaskUpdate model with optional fields to update
        db: AsyncIOMotorDatabase instance for MongoDB operations

    Returns:
        Updated Task model, or None if task not found

    Raises:
        ValueError: If update_data is None
    """
    # Validate update_data is provided
    if update_data is None:
        raise ValueError("update_data cannot be None")

    # Find existing task first
    try:
        existing_task = await db.tasks.find_one({"_id": ObjectId(task_id)})
    except Exception:
        # Invalid ObjectId format or database error
        return None

    if not existing_task:
        # Task not found
        return None

    # Build update dict with only non-None fields from update_data
    update_dict = {}
    if update_data.title is not None:
        update_dict["title"] = update_data.title
    if update_data.description is not None:
        update_dict["description"] = update_data.description
    if update_data.assignee_id is not None:
        update_dict["assignee_id"] = update_data.assignee_id
    if update_data.priority is not None:
        update_dict["priority"] = update_data.priority
    if update_data.status is not None:
        update_dict["status"] = update_data.status
    if update_data.due_date is not None:
        update_dict["due_date"] = update_data.due_date
    if update_data.tags is not None:
        update_dict["tags"] = update_data.tags

    # Add updated_at timestamp
    update_dict["updated_at"] = datetime.utcnow()

    # Update the task in database
    await db.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": update_dict})

    # Fetch and return the updated task
    updated_task_dict = await db.tasks.find_one({"_id": ObjectId(task_id)})
    if updated_task_dict:
        updated_task_dict["id"] = str(updated_task_dict["_id"])
        return Task(**updated_task_dict)

    return None


async def delete_task(task_id: str, db: AsyncIOMotorDatabase) -> bool:
    """
    Delete a task by ID.

    Validates task_id is not empty, deletes the task from MongoDB,
    and returns success status.

    Args:
        task_id: The ID of the task to delete
        db: AsyncIOMotorDatabase instance for MongoDB operations

    Returns:
        True if task was deleted, False if not found or invalid ObjectId

    Raises:
        ValueError: If task_id is empty
    """
    # Validate task_id is not empty
    if not task_id:
        raise ValueError("task_id cannot be empty")

    try:
        # Delete the task from database
        result = await db.tasks.delete_one({"_id": ObjectId(task_id)})

        # Return True if deleted_count >= 1, False if 0
        return result.deleted_count >= 1
    except Exception:
        # Invalid ObjectId format or database error
        return False


async def list_tasks(
    list_id: str,
    db: AsyncIOMotorDatabase,
    skip: Optional[int] = None,
    limit: Optional[int] = None,
) -> List[Task]:
    """
    List all tasks for a given list_id with optional pagination.

    Queries MongoDB tasks by list_id, applies pagination using skip/limit
    if provided, and returns list of Task objects.

    Args:
        list_id: The ID of the list to fetch tasks for
        db: AsyncIOMotorDatabase instance for MongoDB operations
        skip: Optional number of documents to skip (for pagination)
        limit: Optional maximum number of documents to return (for pagination)

    Returns:
        List of Task objects, or empty list if no tasks found
    """
    # Build query
    query = {"list_id": list_id}

    # Convert cursor to list and apply pagination on list
    cursor = db.tasks.find(query)
    tasks = await cursor.to_list(length=limit or 100)

    # Apply pagination (skip/limit) on the list
    if skip is not None:
        tasks = tasks[skip:]
    if limit is not None:
        tasks = tasks[:limit]

    # Convert each task dict to Task model
    result = []
    for task_dict in tasks:
        task_dict["id"] = str(task_dict["_id"])
        result.append(Task(**task_dict))

    return result


async def filter_by_status(
    list_id: str, status: Union[TaskStatus, List[TaskStatus]], db: AsyncIOMotorDatabase
) -> List[Task]:
    """
    Filter tasks by status for a given list_id.

    Queries MongoDB tasks by list_id and status, supporting both single status
    and list of statuses. Returns list of Task objects matching the criteria.

    Args:
        list_id: The ID of the list to filter tasks for
        status: Single TaskStatus or list of TaskStatus to filter by
        db: AsyncIOMotorDatabase instance for MongoDB operations

    Returns:
        List of Task objects matching the status criteria, or empty list if no matches

    Raises:
        ValueError: If status is None or empty list
    """
    # Validate status is not None
    if status is None:
        raise ValueError("status cannot be None")

    # Validate status is not empty list
    if isinstance(status, list) and len(status) == 0:
        raise ValueError("status list cannot be empty")

    # Build query with list_id filter
    query = {"list_id": list_id}

    # Add status filter based on status type
    if isinstance(status, list):
        # Handle list of statuses using $in operator
        query["status"] = {"$in": [s.value for s in status]}
    elif isinstance(status, TaskStatus):
        # Handle single status (use enum value directly, TaskStatus is string enum)
        query["status"] = status
    elif isinstance(status, str):
        # Handle status string (MongoDB will filter on string value directly)
        query["status"] = status

    # Query MongoDB
    cursor = db.tasks.find(query)
    tasks = await cursor.to_list(length=100)

    # Convert each task dict to Task model
    result = []
    for task_dict in tasks:
        task_dict["id"] = str(task_dict["_id"])
        result.append(Task(**task_dict))

    return result


async def transition_task_status(
    task_id: str, new_status: TaskStatus, db: AsyncIOMotorDatabase
) -> Optional[Task]:
    """
    Update task status with validation and state machine rules.

    Args:
        task_id: The ID of the task to transition
        new_status: New status to set (OPEN, IN_PROGRESS, DONE)
        db: AsyncIOMotorDatabase instance for MongoDB operations

    Returns:
        Updated Task object with new status and updated_at timestamp,
        or None if task not found

    Raises:
        ValueError: If new_status is None
        InvalidTransitionError: If transition is invalid (backward or undefined status)
    """
    # Validate new_status
    if new_status is None:
        raise ValueError("new_status cannot be None")

    # Find existing task first
    try:
        existing_task_dict = await db.tasks.find_one({"_id": ObjectId(task_id)})
    except Exception:
        # Invalid ObjectId or database error
        return None

    if not existing_task_dict:
        # Task not found
        return None

    # Extract current status from the task
    current_status = existing_task_dict.get("status")
    if current_status is None:
        current_status = TaskStatus.OPEN
    # Convert string status to TaskStatus enum if needed
    if isinstance(current_status, str):
        try:
            current_status = TaskStatus(current_status)
        except ValueError:
            current_status = TaskStatus.OPEN

    # Define valid transitions (forward only) - use string values for comparison
    valid_transitions = {
        TaskStatus.OPEN.value: [TaskStatus.IN_PROGRESS.value, TaskStatus.DONE.value],
        TaskStatus.IN_PROGRESS.value: [TaskStatus.DONE.value],
        TaskStatus.DONE.value: [],  # Terminal state - no further transitions
    }

    # Check if transition is valid
    if new_status.value not in valid_transitions.get(current_status.value, []):
        raise InvalidTransitionError(
            f"Invalid transition from {current_status.value} to {new_status.value}. "
            f"Valid transitions are: {valid_transitions}"
        )

    # Update task document
    update_dict = {"status": new_status.value, "updated_at": datetime.utcnow()}
    await db.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": update_dict})

    # Fetch and return updated task
    updated_task_dict = await db.tasks.find_one({"_id": ObjectId(task_id)})
    if updated_task_dict:
        updated_task_dict["id"] = str(updated_task_dict["_id"])
        return Task(**updated_task_dict)
    return None
