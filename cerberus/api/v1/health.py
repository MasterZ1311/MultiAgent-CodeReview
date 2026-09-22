"""
Health and Readiness Probes.
No authentication required to allow monitoring systems, k8s, and load balancers to poll.
"""

import time
from datetime import datetime, timezone
from fastapi import APIRouter
from cerberus import __version__
from cerberus.config import settings
from cerberus.core.cache import cache_manager
from cerberus.models.schemas import HealthResponse

router = APIRouter(tags=["Health"])
START_TIME = time.time()


@router.get("/api/v1/health", response_model=HealthResponse)
@router.get("/health", response_model=HealthResponse)
async def health_check():
    """System liveness health check."""
    return HealthResponse(
        status="healthy",
        version=__version__,
        timestamp=datetime.now(timezone.utc).isoformat(),
        database="connected",
        cache="redis" if cache_manager.redis_client else "in_memory_lru",
        active_agents=settings.enabled_agents_list,
        uptime_seconds=round(time.time() - START_TIME, 2),
    )


@router.get("/api/v1/ready")
@router.get("/ready")
async def readiness_check():
    """System readiness probe for traffic routing."""
    return {"status": "ready"}
