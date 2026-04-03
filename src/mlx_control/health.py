"""Health contracts for the internal ``mlx_control`` module."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple


class HealthStatus(str, Enum):
    """Normalized health status for local control summaries."""

    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass(frozen=True)
class HealthCheck:
    """Typed health signal that can be aggregated into a summary."""

    name: str
    status: HealthStatus
    detail: Optional[str] = None


@dataclass(frozen=True)
class HealthSummary:
    """Summarized health view for the controller and state owner."""

    status: HealthStatus = HealthStatus.UNKNOWN
    summary: str = "health unknown"
    checks: Tuple[HealthCheck, ...] = field(default_factory=tuple)
