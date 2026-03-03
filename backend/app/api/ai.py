"""
AI API - FastAPI endpoints for AI-powered task suggestions.

This module provides REST API endpoints for:
1. Task suggestion generation
2. Task prioritization
3. Feedback telemetry collection
"""

import logging
from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse

from app.models.ai import (
    AISuggestionRequest,
    AISuggestionResponse,
    TaskPriorityRequest,
    TaskPriorityResponse,
    FeedbackRequest,
    FeedbackResponse,
    ErrorResponse
)
from app.services.classifier_service import classify_task
from app.services.cache_service import get_or_generate_suggestion
from app.db.database import get_redis

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/ai", tags=["AI Suggestions"])


# Simple rate limiter (in-memory for MVP)
# In production, use Redis-based rate limiting
rate_limiter: Dict[str, Dict[str, Any]] = {}


def check_rate_limit(workspace_id: str, limit: int = 100, window: int = 60) -> bool:
    """
    Simple in-memory rate limiter.

    Args:
        workspace_id: Workspace identifier
        limit: Max requests per window
        window: Window in seconds

    Returns:
        True if rate limit not exceeded, False otherwise
    """
    from datetime import datetime, timedelta

    now = datetime.utcnow()
    workspace_key = f"rate_limit:{workspace_id}"

    if workspace_key not in rate_limiter:
        rate_limiter[workspace_key] = {"count": 0, "window_start": now}
        return True

    window_data = rate_limiter[workspace_key]
    elapsed = (now - window_data["window_start"]).total_seconds()

    # Reset window if expired
    if elapsed > window:
        rate_limiter[workspace_key] = {"count": 1, "window_start": now}
        return True

    # Check limit
    if window_data["count"] >= limit:
        return False

    # Increment count
    rate_limiter[workspace_key]["count"] += 1
    return True


@router.post("/suggest/task", response_model=AISuggestionResponse)
async def suggest_task(
    request: AISuggestionRequest,
    redis_client = Depends(get_redis)
) -> AISuggestionResponse:
    """
    Generate AI-powered task suggestion.

    Returns a structured task suggestion with rewritten title,
    checklist, priority, due date, confidence, and explanation.
    """
    try:
        # Check rate limit
        workspace_id = request.context.get("workspace_id", "default")
        if not check_rate_limit(workspace_id):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )

        # Try to get or generate suggestion (with caching)
        # Handle Redis connection errors gracefully
        try:
            suggestion = await get_or_generate_suggestion(
                request.raw_title,
                request.raw_description,
                request.context,
                redis_client,
                classify_task
            )
        except Exception as cache_error:
            # Fallback: generate suggestion without caching
            logger.warning(f"Cache error, generating without cache: {cache_error}")
            suggestion = await classify_task(
                request.raw_title,
                request.raw_description,
                request.context
            )
            # Add metadata to indicate caching was bypassed
            suggestion["_cache_hit"] = False
            suggestion["_cache_bypass_reason"] = str(cache_error)

        # Return as response (exclude internal metadata fields)
        return AISuggestionResponse(
            rewritten_title=suggestion["rewritten_title"],
            checklist=suggestion["checklist"],
            suggested_priority=suggestion["suggested_priority"],
            suggested_due_date=suggestion.get("suggested_due_date"),
            confidence=suggestion["confidence"],
            explanation=suggestion["explanation"]
        )

    except HTTPException:
        # Re-raise HTTP exceptions (rate limiting, etc.)
        raise
    except ValueError as e:
        # Validation errors
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Unexpected errors - return 500
        logger.error(f"Unexpected error in suggest_task: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

        # Get or generate suggestion (with caching)
        suggestion = await get_or_generate_suggestion(
            request.raw_title,
            request.raw_description,
            request.context,
            redis_client,
            classify_task
        )

        # Return as response (exclude internal metadata fields)
        return AISuggestionResponse(
            rewritten_title=suggestion["rewritten_title"],
            checklist=suggestion["checklist"],
            suggested_priority=suggestion["suggested_priority"],
            suggested_due_date=suggestion.get("suggested_due_date"),
            confidence=suggestion["confidence"],
            explanation=suggestion["explanation"]
        )

    except HTTPException:
        # Re-raise HTTP exceptions (rate limiting, etc.)
        raise
    except ValueError as e:
        # Validation errors
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error in suggest_task: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/prioritize", response_model=TaskPriorityResponse)
async def prioritize_tasks(request: TaskPriorityRequest) -> TaskPriorityResponse:
    """
    Compute effective priority for tasks given context.

    Prioritizes tasks based on priority, due date, and context.
    Returns a prioritized task list.
    """
    try:
        # Sort tasks by priority (higher first) and due date (earlier first)
        tasks = request.tasks.copy()

        # Add calculated priority weight
        # Priority weight: 5 (highest) to 1 (lowest)
        # Due date weight: earlier = higher priority
        current_date = datetime.fromisoformat(request.context.get("current_date", datetime.utcnow().isoformat()))

        def calculate_task_weight(task: Dict[str, Any]) -> float:
            """Calculate task weight for sorting."""
            priority_weight = task.get("priority", 3) * 100  # Priority is most important
            due_date_str = task.get("due_date")

            if due_date_str:
                try:
                    due_date = datetime.fromisoformat(due_date_str)
                    days_until = (due_date - current_date).days
                    # Later due dates = lower weight
                    if days_until < 0:
                        overdue_weight = 1000  # Overdue tasks get highest weight
                    else:
                        overdue_weight = max(0, 30 - days_until)  # Tasks due soon get higher weight
                except (ValueError, TypeError):
                    overdue_weight = 0
            else:
                overdue_weight = 0

            return priority_weight + overdue_weight

        # Calculate weights and sort
        task_weights = [
            (task, calculate_task_weight(task))
            for task in tasks
        ]

        # Sort by weight descending
        sorted_tasks = sorted(task_weights, key=lambda x: x[1], reverse=True)
        prioritized_tasks = [task for task, weight in sorted_tasks]

        # Find suggested next task (highest weight)
        suggested_index = 0
        if prioritized_tasks:
            # Find the requested task in the prioritized list
            for idx, task in enumerate(prioritized_tasks):
                if task.get("id") == request.task_id:
                    suggested_index = idx
                    break

        return TaskPriorityResponse(
            prioritized_tasks=prioritized_tasks,
            suggested_task_index=suggested_index,
            total_count=len(prioritized_tasks)
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error in prioritize_tasks: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/train/feedback", response_model=FeedbackResponse)
async def record_feedback(request: FeedbackRequest) -> FeedbackResponse:
    """
    Record feedback for AI suggestions (telemetry).

    Captures user acceptance/rejection of suggestions for model training.
    """
    try:
        # Validate feedback timestamp
        feedback_at = request.feedback_at or datetime.utcnow().isoformat()

        # In production, store feedback in database
        # For MVP, we'll just log it
        logger.info(
            f"AI Feedback recorded: "
            f"suggestion_id={request.suggestion_id}, "
            f"task_id={request.task_id}, "
            f"user_id={request.user_id}, "
            f"workspace_id={request.workspace_id}, "
            f"accepted={request.accepted}, "
            f"edit_distance={request.edit_distance}, "
            f"feedback_at={feedback_at}"
        )

        # In a real implementation, you would:
        # 1. Store feedback in database
        # 2. Invalidate cache for this task
        # 3. Schedule model retraining

        return FeedbackResponse(
            message="Feedback recorded successfully",
            recorded=True
        )

    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error in record_feedback: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.

    Returns status of AI service.
    """
    return {"status": "healthy"}
