"""Configuration contracts for the internal ``mlx_control`` module."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass(frozen=True)
class ControlConfig:
    """Python-first configuration shape for controller and state contracts.

    The configuration is intentionally small and transportable so the package
    remains extraction-safe and free of CLI or process-launch assumptions.
    """

    default_model_id: Optional[str] = None
    health_checks_enabled: bool = True
    metadata: Dict[str, str] = field(default_factory=dict)
