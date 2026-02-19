from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum
from app.core.config import settings


class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    GUEST = "guest"


class TaskStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class Priority(int, Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    URGENT = 5


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=settings.PASSWORD_MIN_LENGTH)


class UserInDB(UserBase):
    id: Optional[str] = None
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class User(UserBase):
    id: Optional[str] = None
    created_at: datetime


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class WorkspaceBase(BaseModel):
    name: str


class WorkspaceCreate(WorkspaceBase):
    pass


class Workspace(WorkspaceBase):
    id: Optional[str] = None
    owner_id: str
    member_ids: list[str] = []
    region: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ListBase(BaseModel):
    title: str


class ListCreate(ListBase):
    workspace_id: str


class TaskList(ListBase):
    id: Optional[str] = None
    workspace_id: str
    y_doc_key: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = TaskStatus.OPEN
    due_date: Optional[datetime] = None
    tags: list[str] = []


class TaskCreate(TaskBase):
    list_id: str
    assignee_id: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[str] = None
    priority: Optional[Priority] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None
    tags: Optional[list[str]] = None


class Task(TaskBase):
    id: Optional[str] = None
    list_id: str
    assignee_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AISuggestion(BaseModel):
    task_id: str
    workspace_id: str
    rewritten_title: Optional[str]
    checklist: list[str] = []
    priority: Optional[int]
    due_date: Optional[datetime]
    explanation: str
    confidence: float
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AISuggestionRequest(BaseModel):
    raw_title: str
    raw_description: Optional[str] = None
    context: Optional[dict] = None


class AISuggestionResponse(AISuggestion):
    id: Optional[str] = None
    accepted: bool = False
