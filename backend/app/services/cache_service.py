"""
Cache Service - Redis caching for AI suggestions.

This service provides fast caching of task suggestions using Redis,
with configurable TTL (Time To Live) and cache invalidation support.
"""

import hashlib
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional


# Cache key prefix
CACHE_KEY_PREFIX = "ai:suggestion:"

# TTL (Time To Live) in seconds - 24 hours per PRD
CACHE_TTL_SECONDS = 86400  # 24 * 60 * 60

# Hash algorithm
HASH_ALGORITHM = "sha256"


def generate_cache_key(
    raw_title: str,
    raw_description: str,
    context: Dict[str, Any]
) -> str:
    """
    Generate cache key using hash of input parameters.

    Args:
        raw_title: The raw task title
        raw_description: The raw task description
        context: Additional context (workspace_id, current_date, etc.)

    Returns:
        Cache key string (SHA-256 hash)
    """
    # Create a normalized string from inputs
    # Use workspace_id to isolate caches by workspace
    workspace_id = context.get("workspace_id", "default")

    # Create a deterministic string for hashing
    input_string = f"{workspace_id}|{raw_title}|{raw_description}"

    # Generate SHA-256 hash
    hash_obj = hashlib.sha256(input_string.encode('utf-8'))
    hash_hex = hash_obj.hexdigest()

    # Add prefix to identify this as an AI suggestion cache key
    return f"{CACHE_KEY_PREFIX}{hash_hex}"


def get_cached_suggestion(
    raw_title: str,
    raw_description: str,
    context: Dict[str, Any],
    redis_client: Any
) -> Optional[Dict[str, Any]]:
    """
    Retrieve cached suggestion if available.

    Args:
        raw_title: The raw task title
        raw_description: The raw task description
        context: Additional context
        redis_client: Redis client instance (synchronous)

    Returns:
        Cached suggestion dict or None if not found (cache miss)
    """
    # Generate cache key
    cache_key = generate_cache_key(raw_title, raw_description, context)

    # Try to get from cache (synchronous)
    cached_value = redis_client.get(cache_key)

    if cached_value is None:
        # Cache miss
        return None

    # Parse JSON and return
    try:
        return json.loads(cached_value)
    except (json.JSONDecodeError, TypeError):
        # Invalid JSON - treat as cache miss
        return None


def cache_suggestion(
    raw_title: str,
    raw_description: str,
    context: Dict[str, Any],
    suggestion: Dict[str, Any],
    redis_client: Any
) -> None:
    """
    Cache a suggestion with TTL.

    Args:
        raw_title: The raw task title
        raw_description: The raw task description
        context: Additional context
        suggestion: Suggestion dictionary to cache
        redis_client: Redis client instance (synchronous)
    """
    # Generate cache key
    cache_key = generate_cache_key(raw_title, raw_description, context)

    # Serialize suggestion to JSON
    # Remove internal metadata fields before caching
    suggestion_to_cache = {
        k: v for k, v in suggestion.items()
        if not k.startswith('_')  # Don't cache internal metadata
    }

    json_value = json.dumps(suggestion_to_cache)

    # Set in Redis with TTL (synchronous)
    redis_client.setex(cache_key, CACHE_TTL_SECONDS, json_value)


def invalidate_cache(
    raw_title: str,
    raw_description: str,
    context: Dict[str, Any],
    redis_client: Any
) -> None:
    """
    Invalidate cached suggestion.

    Args:
        raw_title: The raw task title
        raw_description: The raw task description
        context: Additional context
        redis_client: Redis client instance (synchronous)
    """
    # Generate cache key
    cache_key = generate_cache_key(raw_title, raw_description, context)

    # Delete from Redis (synchronous)
    redis_client.delete(cache_key)


def get_cache_stats(redis_client: Any) -> Dict[str, Any]:
    """
    Get cache statistics (for monitoring).

    Args:
        redis_client: Redis client instance

    Returns:
        Dictionary with cache stats
    """
    try:
        # Count keys with our prefix
        pattern = f"{CACHE_KEY_PREFIX}*"
        keys = redis_client.keys(pattern)

        return {
            "cache_key_count": len(keys) if keys else 0,
            "cache_prefix": CACHE_KEY_PREFIX,
            "cache_ttl_seconds": CACHE_TTL_SECONDS
        }
    except Exception:
        # If we can't get stats, return empty stats
        return {
            "cache_key_count": 0,
            "cache_prefix": CACHE_KEY_PREFIX,
            "cache_ttl_seconds": CACHE_TTL_SECONDS
        }


async def get_or_generate_suggestion(
    raw_title: str,
    raw_description: str,
    context: Dict[str, Any],
    redis_client: Any,
    generator_func: callable
) -> Dict[str, Any]:
    """
    Get suggestion from cache or generate new one.

    This is main entry point for cached suggestion retrieval.
    It first tries to get from cache, falling back to generation
    if needed.

    Args:
        raw_title: The raw task title
        raw_description: The raw task description
        context: Additional context
        redis_client: Redis client instance (synchronous)
        generator_func: Async function to generate suggestion (e.g., classify_task)

    Returns:
        Suggestion dictionary with metadata
    """
    # Try to get from cache (synchronous)
    cached = get_cached_suggestion(raw_title, raw_description, context, redis_client)

    if cached is not None:
        # Cache hit - add cache metadata
        cached["_cache_hit"] = True
        cached["_cache_hit_at"] = datetime.utcnow().isoformat()
        return cached

    # Cache miss - generate new suggestion
    start_time = time.perf_counter()
    suggestion = await generator_func(raw_title, raw_description, context)
    end_time = time.perf_counter()

    # Add metadata
    suggestion["_cache_hit"] = False
    suggestion["_generation_time_ms"] = round((end_time - start_time) * 1000, 2)

    # Cache new suggestion (synchronous)
    cache_suggestion(raw_title, raw_description, context, suggestion, redis_client)

    return suggestion
