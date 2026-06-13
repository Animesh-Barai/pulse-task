from typing import Optional, List, Union
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.models import Task, TaskCreate, TaskUpdate, TaskStatus, Priority
from bson.objectid import ObjectId
from pydantic import ValidationError

class InvalidTransitionError(Exception):
    pass

async def create_task(task_data: TaskCreate, db: AsyncIOMotorDatabase) -> Task:
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
    result = await db.tasks.insert_one(task_dict)
    return Task(
        id=str(result.inserted_id),
        **task_dict
    )

async def get_task_by_id(task_id: str, db: AsyncIOMotorDatabase) -> Optional[Task]:
    try:
        try:
            oid = ObjectId(task_id)
        except Exception:
            oid = task_id
        task_dict = await db.tasks.find_one({"_id": oid})
        if task_dict:
            task_dict["id"] = str(task_dict["_id"])
            return Task(**task_dict)
    except Exception:
        pass
    return None

async def update_task(task_id: str, update_data: TaskUpdate, db: AsyncIOMotorDatabase) -> Optional[Task]:
    if update_data is None: return None
    try:
        oid = ObjectId(task_id)
    except Exception:
        oid = task_id
        
    # Check if task exists
    task_dict = await db.tasks.find_one({"_id": oid})
    if not task_dict:
        return None
        
    update_dict = {k: v for k, v in update_data.dict(exclude_unset=True).items() if v is not None}
    update_dict["updated_at"] = datetime.utcnow()
    
    await db.tasks.update_one({"_id": oid}, {"$set": update_dict})
    
    # Update dictionary in place
    for k, v in update_dict.items():
        task_dict[k] = v
    task_dict["id"] = str(task_dict["_id"])
    return Task(**task_dict)

async def delete_task(task_id: str, db: AsyncIOMotorDatabase) -> bool:
    try:
        try:
            oid = ObjectId(task_id)
        except Exception:
            oid = task_id
        result = await db.tasks.delete_one({"_id": oid})
        return result.deleted_count >= 1
    except Exception:
        return False

async def list_tasks(
    list_id: str,
    db: AsyncIOMotorDatabase,
    status: Optional[TaskStatus] = None,
    priority: Optional[Priority] = None,
    sort: Optional[str] = None,
    skip: Optional[int] = 0,
    limit: Optional[int] = 100,
) -> List[Task]:
    query = {"list_id": list_id}
    if status: query["status"] = status
    if priority: query["priority"] = priority
    
    cursor = db.tasks.find(query)
    
    if sort:
        sort_field = sort.lstrip('-')
        sort_dir = -1 if sort.startswith('-') else 1
        cursor = cursor.sort(sort_field, sort_dir)
    else:
        cursor = cursor.sort("created_at", -1)
        
    tasks_dicts = await cursor.skip(skip or 0).to_list(length=limit or 100)
    
    result = []
    for td in tasks_dicts:
        try:
            td["id"] = str(td["_id"])
            result.append(Task(**td))
        except Exception:
            continue
    return result

async def filter_by_status(
    list_id: str,
    status: Union[TaskStatus, str, List[Union[TaskStatus, str]]],
    db: AsyncIOMotorDatabase
) -> List[Task]:
    if not isinstance(status, list):
        statuses = [status]
    else:
        statuses = status
        
    valid_statuses = []
    for s in statuses:
        if isinstance(s, TaskStatus):
            valid_statuses.append(s.value)
        elif isinstance(s, str):
            try:
                valid_statuses.append(TaskStatus(s).value)
            except ValueError:
                valid_statuses.append(s)
                
    if len(valid_statuses) == 1:
        query = {"list_id": list_id, "status": valid_statuses[0]}
    else:
        query = {"list_id": list_id, "status": {"$in": valid_statuses}}
        
    cursor = db.tasks.find(query)
    cursor = cursor.sort("created_at", -1)
    tasks_dicts = await cursor.to_list(length=100)
    
    result = []
    for td in tasks_dicts:
        try:
            td["id"] = str(td["_id"])
            result.append(Task(**td))
        except Exception:
            continue
    return result

async def sort_by_created_date(
    list_id: str,
    direction: str,
    db: AsyncIOMotorDatabase
) -> List[Task]:
    if direction not in ("asc", "desc"):
        raise ValueError("Invalid direction. Must be 'asc' or 'desc'")
        
    query = {"list_id": list_id}
    cursor = db.tasks.find(query)
    
    sort_dir = 1 if direction == "asc" else -1
    cursor = cursor.sort("created_at", sort_dir)
    
    tasks_dicts = await cursor.to_list(length=100)
    
    tasks = []
    for td in tasks_dicts:
        try:
            td["id"] = str(td["_id"])
            tasks.append(Task(**td))
        except Exception:
            continue
            
    def get_created_at(task):
        if task.created_at is None:
            return datetime.min if direction == "asc" else datetime.max
        return task.created_at
        
    tasks.sort(key=get_created_at, reverse=(direction == "desc"))
    return tasks

async def transition_task_status(
    task_id: str,
    new_status: Union[TaskStatus, str],
    db: AsyncIOMotorDatabase
) -> Optional[Task]:
    try:
        oid = ObjectId(task_id)
    except Exception:
        oid = task_id
        
    # Find existing task first
    task_dict = await db.tasks.find_one({"_id": oid})
    if not task_dict:
        return None
        
    # Check if new_status is valid
    if isinstance(new_status, str):
        try:
            new_status = TaskStatus(new_status)
        except ValueError:
            raise InvalidTransitionError("Invalid status")
    elif not isinstance(new_status, TaskStatus):
        raise InvalidTransitionError("Invalid status")
        
    current_status = TaskStatus(task_dict["status"])
    
    status_order = {
        TaskStatus.OPEN: 0,
        TaskStatus.IN_PROGRESS: 1,
        TaskStatus.DONE: 2
    }
    
    if status_order[new_status] <= status_order[current_status]:
        raise InvalidTransitionError("Invalid transition: status can only transition forward")
        
    update_dict = {
        "status": new_status.value,
        "updated_at": datetime.utcnow()
    }
    await db.tasks.update_one({"_id": oid}, {"$set": update_dict})
    
    # Update dict in place
    for k, v in update_dict.items():
        task_dict[k] = v
    task_dict["id"] = str(task_dict["_id"])
    return Task(**task_dict)
