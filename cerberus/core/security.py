"""
Security, API Key Generation, Authentication, and Rate Limiting.
"""

import hashlib
import secrets
import time
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
from cerberus.config import settings


def generate_api_key(name: str = "default") -> Tuple[str, str, str]:
    """
    Generates a secure API key.
    Returns: (raw_key, key_hash, prefix)
    """
    token = secrets.token_hex(24)
    prefix = settings.API_KEY_PREFIX
    raw_key = f"{prefix}{token}"
    key_hash = hash_api_key(raw_key)
    return raw_key, key_hash, prefix


def hash_api_key(key: str) -> str:
    """Computes SHA-256 hash of API key for safe database storage."""
    return hashlib.sha256(f"{settings.SECRET_KEY}:{key}".encode("utf-8")).hexdigest()


class RateLimiter:
    """Sliding-window in-memory rate limiter."""
    def __init__(self, limit_per_hour: int = 100):
        self.limit = limit_per_hour
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, identifier: str) -> Tuple[bool, int, int]:
        """
        Check whether request is permitted.
        Returns: (allowed, remaining, retry_after_seconds)
        """
        now = time.time()
        one_hour_ago = now - 3600
        
        # Prune older timestamps
        self.requests[identifier] = [ts for ts in self.requests[identifier] if ts > one_hour_ago]

        current_count = len(self.requests[identifier])
        if current_count >= self.limit:
            oldest_ts = self.requests[identifier][0]
            retry_after = int(oldest_ts + 3600 - now) + 1
            return False, 0, max(1, retry_after)

        self.requests[identifier].append(now)
        remaining = self.limit - (current_count + 1)
        return True, remaining, 0


# Singleton rate limiter
rate_limiter = RateLimiter(limit_per_hour=settings.RATE_LIMIT_PER_HOUR)
