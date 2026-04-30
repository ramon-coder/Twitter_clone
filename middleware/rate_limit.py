"""
Rate Limiting Middleware for Subscription and Recurring Payments Management System

This module provides rate limiting functionality to protect authentication endpoints
from brute force attacks. It uses an in-memory store for development and can be
configured to use Redis in production.
"""

import time
from typing import Dict, Tuple, Optional
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class RateLimitStore:
    """In-memory rate limit store (use Redis in production)"""

    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)
        self._lock = None

    def is_rate_limited(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> Tuple[bool, Optional[int]]:
        """
        Check if a key is rate limited.

        Args:
            key: Unique identifier (e.g., IP address, user ID)
            max_requests: Maximum number of requests allowed in window
            window_seconds: Time window in seconds

        Returns:
            Tuple of (is_limited, retry_after_seconds)
        """
        now = time.time()
        window_start = now - window_seconds

        # Clean old requests outside the window
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > window_start
        ]

        # Check if limit exceeded
        if len(self.requests[key]) >= max_requests:
            retry_after = int(window_seconds - (now - min(self.requests[key])))
            return True, max(1, retry_after)

        # Add current request
        self.requests[key].append(now)
        return False, None


# Global rate limit store
_rate_limit_store = RateLimitStore()


def rate_limit(
    max_requests: int = 5,
    window_seconds: int = 60,
    key_func=None
):
    """
    Rate limiting dependency.

    Args:
        max_requests: Maximum number of requests allowed in window
        window_seconds: Time window in seconds
        key_func: Function to extract rate limit key from request (default: IP address)
    """

    async def default_key_func(request: Request) -> str:
        """Get client IP address as rate limit key"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    key_func = key_func or default_key_func

    async def dependency(request: Request):
        key = await key_func(request)
        is_limited, retry_after = _rate_limit_store.is_rate_limited(
            key, max_requests, window_seconds
        )

        if is_limited:
            logger.warning(f"Rate limit exceeded for key: {key}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {retry_after} seconds",
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(max_requests),
                    "X-RateLimit-Remaining": "0"
                }
            )

        # Add rate limit headers to response
        remaining = max_requests - len(_rate_limit_store.requests[key])
        request.state.rate_limit_remaining = remaining
        request.state.rate_limit_window = window_seconds

    return dependency


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to add rate limit headers to responses"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Add rate limit headers if available
        if hasattr(request.state, "rate_limit_remaining"):
            response.headers["X-RateLimit-Remaining"] = str(request.state.rate_limit_remaining)
            response.headers["X-RateLimit-Window"] = str(request.state.rate_limit_window)

        return response
