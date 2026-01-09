"""
API Middleware - Common middleware for API routes.

Provides authentication, rate limiting, and other cross-cutting concerns.
"""
import time
import logging
from typing import Callable, Optional
from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()


async def auth_middleware(request: Request, call_next: Callable) -> Response:
    """
    Authentication middleware.

    Validates JWT tokens for protected routes.
    """
    # Skip auth for health checks and docs
    if request.url.path in ["/health", "/ready", "/docs", "/openapi.json"]:
        return await call_next(request)

    # Check for Authorization header
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        # Allow unauthenticated access to public routes
        # (route-level auth will handle this)
        return await call_next(request)

    try:
        # Validate token (simplified - implement proper JWT validation)
        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )

        token = auth_header.split(" ")[1]

        # TODO: Implement proper JWT validation
        # For now, just check if token exists
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        # Add user info to request state
        request.state.user = {"id": "user-123", "token": token}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

    return await call_next(request)


async def rate_limit_middleware(request: Request, call_next: Callable) -> Response:
    """
    Rate limiting middleware.

    Limits requests per client.
    """
    # TODO: Implement proper rate limiting with Redis
    # For now, just pass through
    return await call_next(request)


async def timing_middleware(request: Request, call_next: Callable) -> Response:
    """
    Request timing middleware.

    Adds timing information to response headers.
    """
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    return response


async def error_handler_middleware(request: Request, call_next: Callable) -> Response:
    """
    Error handling middleware.

    Catches and formats errors consistently.
    """
    try:
        return await call_next(request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unhandled error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
