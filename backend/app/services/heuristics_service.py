"""
Heuristics Service - Rule-based AI suggestion generation.

This service uses regex and rule-based parsers to generate task suggestions
without requiring external ML models. It's fast, deterministic, and
dependency-free.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional


# Constants for priority mapping
PRIORITY_KEYWORDS = {
    "urgent": 5,
    "asap": 5,
    "critical": 5,
    "emergency": 5,
    "immediate": 5,
    "high": 4,
    "important": 4,
    "medium": 3,
    "low": 2,
    "nice to have": 1,
    "optional": 1,
}

# Weekday mapping for date calculations
WEEKDAY_MAP = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

# Confidence scoring constants
CONFIDENCE_MAX_SCORE = 5.0

# Date offset constants
ASAP_DAYS = 1
URGENT_DAYS = 2
NEXT_WEEK_DAYS = 7

# Action verbs for title rewriting
ACTION_VERBS = [
    "implement", "create", "add", "fix", "update", "improve", "deploy",
    "refactor", "test", "document", "configure", "optimize", "debug",
    "analyze", "design", "build", "integrate", "migrate", "setup", "complete"
]

# Checklist templates based on common task patterns
CHECKLIST_TEMPLATES = {
    "implement": [
        "Draft implementation plan",
        "Write code",
        "Write unit tests",
        "Code review",
        "Merge to main"
    ],
    "fix": [
        "Reproduce the issue",
        "Identify root cause",
        "Implement fix",
        "Write regression test",
        "Verify fix"
    ],
    "test": [
        "Define test cases",
        "Write test code",
        "Run tests",
        "Review test coverage",
        "Document test results"
    ],
    "document": [
        "Gather requirements",
        "Draft documentation",
        "Review with team",
        "Finalize documentation",
        "Publish"
    ],
    "deploy": [
        "Prepare deployment checklist",
        "Stage changes",
        "Run pre-deployment tests",
        "Deploy to production",
        "Verify deployment"
    ]
}


def validate_input(raw_title: Optional[str], raw_description: str) -> None:
    """
    Validate input parameters.

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


def extract_due_date(text: str, current_date: datetime) -> Optional[str]:
    """
    Extract due date from text using patterns.

    Args:
        text: Text to search for date patterns
        current_date: Current date for relative date calculation

    Returns:
        ISO date string (YYYY-MM-DD) or None if no date found
    """
    text_lower = text.lower()

    # Pattern: "by Friday", "by monday", etc. (case-insensitive)
    day_pattern = r"\bby\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b"
    day_match = re.search(day_pattern, text_lower, re.IGNORECASE)

    if day_match:
        day_name = day_match.group(1)
        current_weekday = current_date.weekday()

        days_until = (WEEKDAY_MAP[day_name] - current_weekday) % 7
        if days_until == 0:
            days_until = 7  # Next week, not today

        due_date = current_date + timedelta(days=days_until)
        return due_date.strftime("%Y-%m-%d")

    # Pattern: "ASAP" -> within 24 hours (next business day)
    if re.search(r"\basap\b", text_lower):
        due_date = current_date + timedelta(days=ASAP_DAYS)
        return due_date.strftime("%Y-%m-%d")

    # Pattern: "urgent" -> within 48 hours
    if re.search(r"\burgent\b", text_lower):
        due_date = current_date + timedelta(days=URGENT_DAYS)
        return due_date.strftime("%Y-%m-%d")

    # Pattern: "tomorrow"
    if "tomorrow" in text_lower:
        due_date = current_date + timedelta(days=ASAP_DAYS)
        return due_date.strftime("%Y-%m-%d")

    # Pattern: "next week"
    if "next week" in text_lower:
        due_date = current_date + timedelta(days=NEXT_WEEK_DAYS)
        return due_date.strftime("%Y-%m-%d")

    return None


def detect_priority(text: str) -> int:
    """
    Detect priority from text using keyword matching.

    Args:
        text: Text to search for priority keywords

    Returns:
        Priority level (1-5)
    """
    text_lower = text.lower()

    # Check each priority keyword
    for keyword, priority in PRIORITY_KEYWORDS.items():
        if keyword in text_lower:
            return priority

    # Default priority for tasks without explicit priority keywords
    return 3  # Medium priority


def generate_checklist(raw_title: str, raw_description: str) -> List[str]:
    """
    Generate checklist based on task title and description.

    Args:
        raw_title: The task title
        raw_description: The task description

    Returns:
        List of checklist items
    """
    combined_text = f"{raw_title} {raw_description}".lower()

    # Find matching template based on keywords
    for keyword, template in CHECKLIST_TEMPLATES.items():
        if keyword in combined_text:
            return template.copy()

    # Default checklist for generic tasks
    return [
        "Define scope and requirements",
        "Complete the main task",
        "Review and test",
        "Finalize and document"
    ]


def rewrite_title(raw_title: str) -> str:
    """
    Rewrite title to ensure it starts with an action verb.

    Args:
        raw_title: The raw task title

    Returns:
        Rewritten title with action verb
    """
    title = raw_title.strip()

    # Check if title already starts with an action verb
    title_lower = title.lower()
    for verb in ACTION_VERBS:
        if title_lower.startswith(verb):
            return title.capitalize()

    # Prepend an appropriate action verb
    if "fix" in title_lower or "bug" in title_lower:
        return f"Fix {title}"
    elif "implement" in title_lower or "create" in title_lower or "add" in title_lower:
        return f"Implement {title}"
    elif "authentication" in title_lower or "login" in title_lower or "register" in title_lower:
        return f"Implement {title}"
    else:
        return f"Create {title}"


def calculate_confidence(raw_title: str, raw_description: str) -> float:
    """
    Calculate confidence score based on input clarity.

    Args:
        raw_title: The task title
        raw_description: The task description

    Returns:
        Confidence score (0.0-1.0)
    """
    score = 0.0

    # Title clarity (0-3)
    if raw_title and len(raw_title.strip()) > 5:
        score += 1.0
    if len(raw_title.strip()) > 10:
        score += 1.0
    if any(keyword in raw_title.lower() for keyword in ["implement", "create", "fix", "test", "deploy"]):
        score += 1.0

    # Specificity (0-1)
    combined = f"{raw_title} {raw_description}".lower()
    if any(keyword in combined for keyword in ["api", "database", "authentication", "user", "test", "deploy", "login"]):
        score += 1.0

    # No vague language (0-1)
    vague_terms = ["stuff", "things", "something", "anything", "do stuff"]
    if not any(term in combined for term in vague_terms):
        score += 1.0

    return round(score / CONFIDENCE_MAX_SCORE, 2)


def generate_explanation(raw_title: str, priority: int, has_due_date: bool) -> str:
    """
    Generate explanation for the suggestion.

    Args:
        raw_title: The task title
        priority: Suggested priority
        has_due_date: Whether a due date was detected

    Returns:
        Explanation string
    """
    parts = []

    # Priority explanation
    if priority == 5:
        parts.append("High priority due to urgency keywords")
    elif priority == 4:
        parts.append("High priority task")
    elif priority == 3:
        parts.append("Medium priority task")
    elif priority == 2:
        parts.append("Low priority task")
    else:
        parts.append("Optional task")

    # Due date explanation
    if has_due_date:
        parts.append("due date detected from description")

    # Title clarity explanation
    if len(raw_title.split()) >= 3:
        parts.append("clear task description provided")

    return ". ".join(parts) + "."


async def generate_suggestion(
    raw_title: str,
    raw_description: str,
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate AI suggestion for a task using heuristics.

    Args:
        raw_title: The raw task title
        raw_description: The raw task description
        context: Additional context (workspace_id, current_date, etc.)

    Returns:
        Dictionary containing:
        - rewritten_title: Improved task title
        - checklist: List of actionable steps
        - suggested_priority: Priority level (1-5)
        - suggested_due_date: ISO date string or None
        - confidence: Confidence score (0.0-1.0)
        - explanation: Explanation of the suggestion

    Raises:
        ValueError: If input is invalid
    """
    # Validate input
    validate_input(raw_title, raw_description)

    # Get current date from context or use today
    current_date = context.get("current_date", datetime.now())

    # Combine title and description for pattern matching
    combined_text = f"{raw_title} {raw_description}"

    # Generate suggestion components
    rewritten_title = rewrite_title(raw_title)
    checklist = generate_checklist(raw_title, raw_description)
    suggested_priority = detect_priority(combined_text)
    suggested_due_date = extract_due_date(combined_text, current_date)
    confidence = calculate_confidence(raw_title, raw_description)
    explanation = generate_explanation(raw_title, suggested_priority, suggested_due_date is not None)

    return {
        "rewritten_title": rewritten_title,
        "checklist": checklist,
        "suggested_priority": suggested_priority,
        "suggested_due_date": suggested_due_date,
        "confidence": confidence,
        "explanation": explanation
    }
