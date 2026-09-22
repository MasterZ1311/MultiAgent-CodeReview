"""
FastAPI Dependencies for Authentication, Database Sessions, and Rate Limiting.
"""

from typing import Optional
from fastapi import Header, HTTPException, Request, status
from cerberus.config import settings
from cerberus.core.security import rate_limiter


async def verify_api_key(
    request: Request,
    authorization: Optional[str] = Header(None)
) -> str:
    """
    Validates the API key from the Authorization header.
    Accepts keys with prefix `cvai_` or default developer credentials.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"

    # In local development mode, permit unauthenticated or default key requests
    if settings.ENVIRONMENT == "development" and not authorization:
        # Check rate limit on IP
        allowed, remaining, retry_after = rate_limiter.is_allowed(client_ip)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={"error": "rate_limit_exceeded", "message": f"Rate limit exceeded. Retry in {retry_after}s."},
                headers={"Retry-After": str(retry_after)}
            )
        return "cvai_dev_anonymous"

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "missing_authentication", "message": "No Authorization header provided"}
        )

    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid_token_format", "message": "Authorization must be Bearer <token>"}
        )

    token = parts[1]

    # Validate token prefix or dev key
    if token != settings.DEFAULT_DEV_API_KEY and not token.startswith(settings.API_KEY_PREFIX):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid_api_key", "message": "API key is invalid or has expired"}
        )

    # Check Rate Limit
    allowed, remaining, retry_after = rate_limiter.is_allowed(token)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"error": "rate_limit_exceeded", "message": f"Rate limit exceeded. Retry in {retry_after}s."},
            headers={"Retry-After": str(retry_after)}
        )

    return token
