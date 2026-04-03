"""Health contracts for the internal ``mlx_control`` module."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple

from .exceptions import ControlHealthError


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

    def __post_init__(self) -> None:
        """Validate minimal health-check shape constraints."""

        if not self.name.strip():
            raise ControlHealthError("health check name must be a non-empty string")


@dataclass(frozen=True)
class HealthSummary:
    """Summarized health view for the controller and state owner."""

    status: HealthStatus = HealthStatus.UNKNOWN
    summary: str = "health unknown"
    checks: Tuple[HealthCheck, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Validate summarized health contract coherence."""

        if not self.summary.strip():
            raise ControlHealthError("health summary must be a non-empty string")

        if self.status is HealthStatus.HEALTHY:
            invalid_checks = [check.name for check in self.checks if check.status is not HealthStatus.HEALTHY]
            if invalid_checks:
                raise ControlHealthError(
                    "healthy summary cannot contain non-healthy checks: "
                    + ", ".join(invalid_checks)
                )
