"""
Security, API Key Generation, Authentication, and Rate Limiting.
"""

import hashlib
import secrets
import time
from collections import OrderedDict
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
    """Sliding-window in-memory rate limiter with bounded storage."""
    def __init__(self, limit_per_hour: int = 100, max_tracked: Optional[int] = None):
        self.limit = limit_per_hour
        self.max_tracked = max_tracked if max_tracked is not None else settings.RATE_LIMIT_MAX_TRACKED
        self.requests: OrderedDict[str, List[float]] = OrderedDict()

    def purge_expired(self) -> int:
        """Purge all tracking keys that have no timestamps or whose timestamps are all expired."""
        now = time.time()
        one_hour_ago = now - 3600
        purged = 0
        keys_to_remove = []
        for ident, timestamps in list(self.requests.items()):
            active = [ts for ts in timestamps if ts > one_hour_ago]
            if not active:
                keys_to_remove.append(ident)
            else:
                self.requests[ident] = active
        for ident in keys_to_remove:
            if ident in self.requests:
                del self.requests[ident]
                purged += 1
        return purged

    def is_allowed(self, identifier: str) -> Tuple[bool, int, int]:
        """
        Check whether request is permitted.
        Returns: (allowed, remaining, retry_after_seconds)
        """
        now = time.time()
        one_hour_ago = now - 3600

        # Prune older timestamps
        if identifier in self.requests:
            self.requests[identifier] = [ts for ts in self.requests[identifier] if ts > one_hour_ago]
            if len(self.requests[identifier]) == 0:
                del self.requests[identifier]

        # If identifier not tracked yet and at capacity, run sweep and evict if needed
        if identifier not in self.requests:
            if len(self.requests) >= self.max_tracked:
                self.purge_expired()
                while len(self.requests) >= self.max_tracked and self.requests:
                    self.requests.popitem(last=False)

        current_timestamps = self.requests.get(identifier, [])
        current_count = len(current_timestamps)
        if current_count >= self.limit:
            oldest_ts = current_timestamps[0]
            retry_after = int(oldest_ts + 3600 - now) + 1
            return False, 0, max(1, retry_after)

        if identifier not in self.requests:
            self.requests[identifier] = []
        self.requests[identifier].append(now)
        self.requests.move_to_end(identifier)
        remaining = self.limit - (current_count + 1)
        return True, remaining, 0


# Singleton rate limiter
rate_limiter = RateLimiter(limit_per_hour=settings.RATE_LIMIT_PER_HOUR, max_tracked=settings.RATE_LIMIT_MAX_TRACKED)
