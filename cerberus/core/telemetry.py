"""
Telemetry, Metrics (Prometheus), and Structured Logging.
"""

import logging
import sys
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Configure application-wide logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("cerberus")

# Prometheus Metrics
REVIEW_REQUESTS_TOTAL = Counter(
    "cerberus_review_requests_total",
    "Total number of code review requests processed",
    ["status", "language"]
)

REVIEW_DURATION_SECONDS = Histogram(
    "cerberus_review_duration_seconds",
    "Time spent analyzing code reviews",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

AGENT_EXECUTION_SECONDS = Histogram(
    "cerberus_agent_execution_seconds",
    "Execution duration per agent",
    ["agent_name"],
    buckets=[0.05, 0.2, 0.5, 1.0, 3.0, 8.0]
)

FINDINGS_DETECTED_TOTAL = Counter(
    "cerberus_findings_detected_total",
    "Count of findings discovered by agents",
    ["agent_name", "severity"]
)

CACHE_HITS_TOTAL = Counter(
    "cerberus_cache_hits_total",
    "Number of review requests served directly from cache"
)

CACHE_MISSES_TOTAL = Counter(
    "cerberus_cache_misses_total",
    "Number of review requests requiring fresh agent analysis"
)


def get_prometheus_metrics() -> bytes:
    """Returns serialized Prometheus metrics bytes."""
    return generate_latest()
