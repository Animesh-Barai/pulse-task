from typing import Optional, List, Union
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.models import Task, TaskCreate, TaskUpdate, TaskStatus, Priority
from bson.objectid import ObjectId

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
        task_dict = await db.tasks.find_one({"_id": ObjectId(task_id)})
        if task_dict:
            task_dict["id"] = str(task_dict["_id"])
            return Task(**task_dict)
    except Exception:
        pass
    return None

async def update_task(task_id: str, update_data: TaskUpdate, db: AsyncIOMotorDatabase) -> Optional[Task]:
    if update_data is None: return None
    update_dict = {k: v for k, v in update_data.dict(exclude_unset=True).items() if v is not None}
    update_dict["updated_at"] = datetime.utcnow()
    await db.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": update_dict})
    return await get_task_by_id(task_id, db)

async def delete_task(task_id: str, db: AsyncIOMotorDatabase) -> bool:
    try:
        result = await db.tasks.delete_one({"_id": ObjectId(task_id)})
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
