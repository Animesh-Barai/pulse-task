"""
Classifier Service - Local ML model wrapper for task classification.

This service wraps a local classifier (DistilBERT/scikit-learn) for
task suggestion generation. For MVP, it uses heuristics as a mock model.
Future implementation will integrate actual ML models.
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional

# Import heuristics service for fallback and as mock model
from app.services.heuristics_service import generate_suggestion as heuristics_suggest


# Confidence thresholds (from PRD Section 8.5)
CONFIDENCE_HIGH = 0.8
CONFIDENCE_LOW = 0.5

# Metadata field names for internal tracking
META_LATENCY_MS = "_latency_ms"
META_FALLBACK_USED = "_fallback_used"
META_FALLBACK_REASON = "_fallback_reason"

# Schema constants
REQUIRED_SCHEMA_FIELDS = [
    "rewritten_title",
    "checklist",
    "suggested_priority",
    "suggested_due_date",
    "confidence",
    "explanation"
]

# Value range constants
PRIORITY_MIN = 1
PRIORITY_MAX = 5
CONFIDENCE_MIN = 0.0
CONFIDENCE_MAX = 1.0
DATE_FORMAT_LENGTH = 10


def validate_classifier_input(raw_title: Optional[str], raw_description: str) -> None:
    """
    Validate input parameters for classifier.

    Args:
        raw_title: The raw task title
        raw_description: The raw task description

    Raises:
        ValueError: If input is invalid
    """
    if raw_title is None:
        raise ValueError("Title cannot be None")

    if not isinstance(raw_title, str):
        raise ValueError("Title must be a string")

    if not raw_title.strip():
        raise ValueError("Title cannot be empty")


def validate_field_type(result: Dict[str, Any], field: str, expected_type: type) -> None:
    """
    Validate that a field exists and has the expected type.

    Args:
        result: Result dictionary
        field: Field name to validate
        expected_type: Expected Python type

    Raises:
        ValueError: If field is missing or has wrong type
    """
    if field not in result:
        raise ValueError(f"Missing required field: {field}")

    if not isinstance(result[field], expected_type):
        raise ValueError(f"{field} must be a {expected_type.__name__}")


def validate_date_format(date_str: str) -> None:
    """
    Validate ISO date format (YYYY-MM-DD).

    Args:
        date_str: Date string to validate

    Raises:
        ValueError: If date format is invalid
    """
    if len(date_str) != DATE_FORMAT_LENGTH:
        raise ValueError("suggested_due_date must be in YYYY-MM-DD format")
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError("suggested_due_date must be a valid date")


def validate_output_schema(result: Dict[str, Any]) -> None:
    """
    Validate output schema matches required format.

    Args:
        result: Classification result dictionary

    Raises:
        ValueError: If schema is invalid
    """
    # Validate required fields and types
    validate_field_type(result, "rewritten_title", str)
    validate_field_type(result, "checklist", list)
    validate_field_type(result, "suggested_priority", int)
    validate_field_type(result, "confidence", float)
    validate_field_type(result, "explanation", str)

    # Validate value ranges
    if not (PRIORITY_MIN <= result["suggested_priority"] <= PRIORITY_MAX):
        raise ValueError(f"suggested_priority must be between {PRIORITY_MIN} and {PRIORITY_MAX}")

    if not (CONFIDENCE_MIN <= result["confidence"] <= CONFIDENCE_MAX):
        raise ValueError(f"confidence must be between {CONFIDENCE_MIN} and {CONFIDENCE_MAX}")

    # Validate date format if present
    if result["suggested_due_date"] is not None:
        validate_field_type(result, "suggested_due_date", str)
        validate_date_format(result["suggested_due_date"])


async def mock_classify(
    raw_title: str,
    raw_description: str,
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Mock classifier using heuristics.

    For MVP, this simulates a local ML classifier by using heuristics.
    In production, this would call DistilBERT or scikit-learn model.

    Args:
        raw_title: The raw task title
        raw_description: The raw task description
        context: Additional context

    Returns:
        Classification result dictionary
    """
    # Use heuristics as the mock model
    return await heuristics_suggest(raw_title, raw_description, context)


def add_metadata_to_result(
    result: Dict[str, Any],
    start_time: float,
    fallback_used: bool = False,
    fallback_reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add metadata fields to classification result.

    Args:
        result: Classification result dictionary
        start_time: Start time for latency calculation
        fallback_used: Whether fallback was used
        fallback_reason: Reason for fallback (if any)

    Returns:
        Updated result dictionary with metadata
    """
    end_time = time.perf_counter()
    latency_ms = (end_time - start_time) * 1000

    result[META_LATENCY_MS] = round(latency_ms, 2)

    if fallback_used:
        result[META_FALLBACK_USED] = True
        if fallback_reason:
            result[META_FALLBACK_REASON] = fallback_reason

    return result


async def classify_task(
    raw_title: str,
    raw_description: str,
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Classify task using local classifier (with fallback to heuristics).

    This is the main entry point for task classification. It attempts to use
    a local ML classifier, with graceful fallback to heuristics if needed.

    Args:
        raw_title: The raw task title
        raw_description: The raw task description
        context: Additional context (workspace_id, current_date, force_fallback)

    Returns:
        Dictionary containing:
        - rewritten_title: Improved task title
        - checklist: List of actionable steps
        - suggested_priority: Priority level (1-5)
        - suggested_due_date: ISO date string or None
        - confidence: Confidence score (0.0-1.0)
        - explanation: Explanation of suggestion
        - _latency_ms: Internal latency tracking
        - _fallback_used: Internal fallback tracking

    Raises:
        ValueError: If input is invalid or output schema is invalid
    """
    # Start timer for latency measurement
    start_time = time.perf_counter()

    # Validate input
    validate_classifier_input(raw_title, raw_description)

    # Check if fallback is forced (for testing)
    force_fallback = context.get("force_fallback", False)

    try:
        # Attempt classification using mock classifier
        if not force_fallback:
            result = await mock_classify(raw_title, raw_description, context)
        else:
            raise Exception("Fallback forced for testing")

        # Validate output schema
        validate_output_schema(result)

        # Add metadata (no fallback used)
        return add_metadata_to_result(result, start_time, fallback_used=False)

    except Exception as e:
        # Fallback to heuristics on error
        try:
            result = await heuristics_suggest(raw_title, raw_description, context)
            validate_output_schema(result)

            # Add metadata (with fallback tracking)
            return add_metadata_to_result(
                result,
                start_time,
                fallback_used=True,
                fallback_reason=str(e)
            )

        except Exception as fallback_error:
            # Re-raise if fallback also fails
            raise ValueError(f"Classification failed and fallback also failed: {fallback_error}")
