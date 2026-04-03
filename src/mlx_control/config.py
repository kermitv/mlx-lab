"""Configuration contracts for the internal ``mlx_control`` module."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from .exceptions import ControlConfigError


@dataclass(frozen=True)
class ControlConfig:
    """Python-first configuration shape for controller and state contracts.

    The configuration is intentionally small and transportable so the package
    remains extraction-safe and free of CLI or process-launch assumptions.
    """

    default_model_id: Optional[str] = None
    health_checks_enabled: bool = True
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate transport-safe configuration values."""

        if self.default_model_id is not None and not self.default_model_id.strip():
            raise ControlConfigError("default_model_id must be a non-empty string")

        for key, value in self.metadata.items():
            if not key.strip():
                raise ControlConfigError("metadata keys must be non-empty strings")
            if not value.strip():
                raise ControlConfigError("metadata values must be non-empty strings")
