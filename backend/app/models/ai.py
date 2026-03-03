"""
AI Models - Pydantic models for AI suggestions and API requests/responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class AISuggestionRequest(BaseModel):
    """Request model for AI suggestion endpoint."""

    raw_title: str = Field(..., description="Raw task title", min_length=1)
    raw_description: str = Field(default="", description="Raw task description")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context (workspace_id, current_date, etc.)")

    class Config:
        json_schema_extra = {
            "example": {
                "raw_title": "Implement user authentication",
                "raw_description": "Add OAuth2 login support",
                "context": {
                    "workspace_id": "ws_123",
                    "current_date": "2026-02-26T00:00:00Z"
                }
            }
        }


class AISuggestionResponse(BaseModel):
    """Response model for AI suggestion."""

    rewritten_title: str = Field(..., description="Improved task title")
    checklist: List[str] = Field(..., description="Actionable checklist")
    suggested_priority: int = Field(..., ge=1, le=5, description="Suggested priority (1-5)")
    suggested_due_date: Optional[str] = Field(None, description="Suggested due date (YYYY-MM-DD or null)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    explanation: str = Field(..., description="Explanation of suggestion")

    class Config:
        json_schema_extra = {
            "example": {
                "rewritten_title": "Implement user authentication with OAuth2",
                "checklist": [
                    "Design authentication flow",
                    "Implement login endpoint",
                    "Implement registration endpoint",
                    "Test authentication"
                ],
                "suggested_priority": 5,
                "suggested_due_date": "2026-03-01",
                "confidence": 0.9,
                "explanation": "High confidence - clear task with specific technology"
            }
        }


class TaskPriorityRequest(BaseModel):
    """Request model for prioritization endpoint."""

    task_id: str = Field(..., description="Current task ID")
    tasks: List[Dict[str, Any]] = Field(..., description="List of tasks to prioritize")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_123",
                "tasks": [
                    {"id": "task_1", "priority": 3, "due_date": "2026-03-01"},
                    {"id": "task_2", "priority": 5, "due_date": "2026-02-28"}
                ],
                "context": {
                    "workspace_id": "ws_123",
                    "current_date": "2026-02-26"
                }
            }
        }


class TaskPriorityResponse(BaseModel):
    """Response model for prioritization."""

    prioritized_tasks: List[Dict[str, Any]] = Field(..., description="Prioritized task list")
    suggested_task_index: int = Field(..., ge=0, description="Index of suggested next task")
    total_count: int = Field(..., ge=0, description="Total number of tasks")

    class Config:
        json_schema_extra = {
            "example": {
                "prioritized_tasks": [
                    {"id": "task_2", "priority": 5, "due_date": "2026-02-28"},
                    {"id": "task_1", "priority": 3, "due_date": "2026-03-01"}
                ],
                "suggested_task_index": 0,
                "total_count": 2
            }
        }


class FeedbackRequest(BaseModel):
    """Request model for feedback endpoint."""

    suggestion_id: str = Field(..., description="Suggestion ID")
    task_id: str = Field(..., description="Task ID")
    user_id: str = Field(..., description="User ID")
    workspace_id: str = Field(..., description="Workspace ID")
    accepted: bool = Field(..., description="Whether suggestion was accepted")
    edit_distance: Optional[float] = Field(None, ge=0.0, description="Edit distance between suggested and final version")
    feedback_at: Optional[str] = Field(None, description="Feedback timestamp (ISO format)")

    class Config:
        json_schema_extra = {
            "example": {
                "suggestion_id": "suggestion_123",
                "task_id": "task_456",
                "user_id": "user_789",
                "workspace_id": "ws_123",
                "accepted": True,
                "edit_distance": 0.1,
                "feedback_at": "2026-02-26T10:30:00Z"
            }
        }


class FeedbackResponse(BaseModel):
    """Response model for feedback endpoint."""

    message: str = Field(..., description="Success message")
    recorded: bool = Field(..., description="Whether feedback was recorded")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Feedback recorded successfully",
                "recorded": True
            }
        }


class ErrorResponse(BaseModel):
    """Generic error response model."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid input",
                "detail": "Title cannot be empty"
            }
        }
