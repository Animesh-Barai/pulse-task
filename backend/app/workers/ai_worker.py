"""
AI Background Worker - Celery tasks for async AI processing.

This module provides Celery-based background tasks for:
1. Async task queue processing
2. LLM fallback invocation for complex tasks
3. Retry logic with exponential backoff
4. Comprehensive error logging
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, Callable

# Import Celery (will be initialized in main.py)
try:
    from celery import Celery, Task
except ImportError:
    # Celery not installed - create dummy classes
    class Celery:
        def __init__(self, *args, **kwargs):
            pass

    class Task:
        def __init__(self, *args, **kwargs):
            pass

# Import existing services
from app.services.classifier_service import classify_task
from app.services.cache_service import cache_suggestion, invalidate_cache


# Configure logging
logger = logging.getLogger(__name__)


# Celery app (initialized in main.py)
celery_app: Optional[Celery] = None


def get_celery_app() -> Celery:
    """
    Get or initialize Celery app.

    Returns:
        Celery app instance
    """
    global celery_app
    if celery_app is None:
        # For MVP, we're using a mock Celery app
        # In production, configure with actual Redis broker
        celery_app = Celery('pulsetasks')

    return celery_app


async def process_ai_task(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process AI task asynchronously.

    Args:
        task_data: Dictionary containing task_id, raw_title, raw_description, context

    Returns:
        Result dictionary with status and result data
    """
    task_id = task_data.get("task_id")
    raw_title = task_data.get("raw_title", "")
    raw_description = task_data.get("raw_description", "")
    context = task_data.get("context", {})

    try:
        # Set status to processing
        result = {
            "status": "processing",
            "task_id": task_id,
            "started_at": datetime.utcnow().isoformat()
        }

        logger.info(f"Processing AI task: {task_id}")

        # Generate suggestion using classifier (with caching)
        redis_client = None  # Would use get_redis() in production
        suggestion = await classify_task(raw_title, raw_description, context)

        # Cache the result
        if redis_client:
            cache_suggestion(raw_title, raw_description, context, suggestion, redis_client)

        # Update result with success
        result.update({
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat(),
            "suggestion": suggestion
        })

        logger.info(f"AI task completed: {task_id}")

        return result

    except Exception as e:
        # Update result with error
        error_result = {
            "status": "failed",
            "task_id": task_id,
            "error": str(e),
            "error_at": datetime.utcnow().isoformat()
        }

        # Log the error
        log_worker_error(task_data, e)

        return error_result


async def process_llm_fallback(task_data: Dict[str, Any], llm_client: Any = None) -> Dict[str, Any]:
    """
    Process LLM fallback for complex tasks.

    For MVP, this is a placeholder. In production, integrate with
    OpenAI or similar LLM provider.

    Args:
        task_data: Dictionary containing task information
        llm_client: Optional LLM client (e.g., OpenAI client)

    Returns:
        Result dictionary with LLM-generated suggestion
    """
    task_id = task_data.get("task_id")
    raw_title = task_data.get("raw_title", "")
    raw_description = task_data.get("raw_description", "")

    logger.info(f"Processing LLM fallback for task: {task_id}")

    try:
        # For MVP: Use heuristics as LLM fallback
        # In production: Call actual LLM API
        if llm_client is None:
            # MVP: Use existing classifier as "LLM"
            context = task_data.get("context", {})
            result = await classify_task(raw_title, raw_description, context)

            return {
                "status": "completed",
                "llm_result": result,
                "llm_provider": "mock",
                "llm_processed_at": datetime.utcnow().isoformat()
            }
        else:
            # Production: Call actual LLM
            # This is a placeholder for actual LLM integration
            logger.warning("LLM client provided but not yet implemented - using heuristics")
            context = task_data.get("context", {})
            suggestion = await classify_task(raw_title, raw_description, context)

            return {
                "status": "completed",
                "llm_result": suggestion,
                "llm_provider": "placeholder",
                "llm_processed_at": datetime.utcnow().isoformat()
            }

    except Exception as e:
        error_result = {
            "status": "failed",
            "task_id": task_id,
            "error": str(e),
            "error_at": datetime.utcnow().isoformat()
        }

        log_worker_error(task_data, e)

        return error_result


async def process_ai_task_with_retry(
    task_data: Dict[str, Any],
    processing_func: Callable,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    backoff_factor: float = 2.0
) -> Dict[str, Any]:
    """
    Process AI task with retry logic (exponential backoff).

    Args:
        task_data: Dictionary containing task information
        processing_func: Async function to call for processing
        max_retries: Maximum number of retry attempts
        retry_delay: Initial delay between retries (seconds)
        backoff_factor: Multiplier for exponential backoff

    Returns:
        Result dictionary with status and result data
    """
    task_id = task_data.get("task_id", "unknown")

    for attempt in range(max_retries + 1):
        try:
            logger.info(f"Processing attempt {attempt + 1}/{max_retries + 1} for task: {task_id}")

            # Call the processing function
            result = await processing_func(task_data)

            # Success - return result
            if attempt > 0:
                logger.info(f"Task {task_id} succeeded on attempt {attempt + 1}")

            return result

        except Exception as e:
            # Log the error
            logger.warning(f"Task {task_id} failed on attempt {attempt + 1}: {e}")

            # Check if this is the last attempt
            if attempt == max_retries:
                # All retries exhausted - return error
                error_result = {
                    "status": "failed",
                    "task_id": task_id,
                    "error": f"All {max_retries + 1} attempts failed: {str(e)}",
                    "error_at": datetime.utcnow().isoformat(),
                    "attempts": attempt + 1
                }

                log_worker_error(task_data, e, is_final=True)

                return error_result

            # Wait before retry with exponential backoff
            delay = retry_delay * (backoff_factor ** attempt)
            logger.info(f"Retrying task {task_id} in {delay:.2f} seconds...")
            await asyncio.sleep(delay)

    # Should never reach here
    return {
        "status": "failed",
        "task_id": task_id,
        "error": "Unexpected error in retry logic"
    }


def log_worker_error(
    task_data: Dict[str, Any],
    error: Exception,
    is_final: bool = False
) -> None:
    """
    Log worker errors with context.

    Args:
        task_data: Dictionary containing task information
        error: The exception that occurred
        is_final: Whether this is the final error after all retries
    """
    task_id = task_data.get("task_id", "unknown")
    error_type = type(error).__name__
    error_message = str(error)

    if is_final:
        logger.error(
            f"Final error for task {task_id} [{error_type}]: {error_message}",
            exc_info=True
        )
    else:
        logger.warning(
            f"Retryable error for task {task_id} [{error_type}]: {error_message}",
            exc_info=True
        )


# Celery task definitions (for production use)
def register_celery_tasks() -> None:
    """
    Register Celery tasks when Celery is configured.

    For MVP, these are placeholder definitions.
    """
    global celery_app
    if celery_app is None:
        logger.warning("Celery not initialized - tasks not registered")
        return

    # Register AI task
    @celery_app.task(name="process_ai_task")
    def process_ai_task_sync(task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronous wrapper for async process_ai_task.
        Celery tasks must be synchronous.
        """
        return asyncio.run(process_ai_task(task_data))

    # Register LLM fallback task
    @celery_app.task(name="process_llm_fallback")
    def process_llm_fallback_sync(task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronous wrapper for async process_llm_fallback.
        """
        return asyncio.run(process_llm_fallback(task_data))

    logger.info("Celery tasks registered")


# Initialize on module load (optional)
register_celery_tasks()
