"""Canonical control-state contracts for the internal ``mlx_control`` module.

This module owns the controller-visible state model for Phase 1. Other modules
may define supporting types, but the aggregate state shape lives here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from .config import ControlConfig
from .exceptions import ControlStateError
from .health import HealthSummary
from .registry import ModelRegistryState


class DesiredControlMode(str, Enum):
    """Target posture requested by the control module."""

    STOPPED = "stopped"
    RUNNING = "running"


class RuntimePhase(str, Enum):
    """Observed local runtime phase as understood by the control module."""

    UNKNOWN = "unknown"
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass(frozen=True)
class ActiveModelIdentity:
    """Canonical model identity exposed to controller consumers."""

    model_id: str
    display_name: Optional[str] = None
    revision: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate the canonical controller-facing model identity."""

        _require_model_id(self.model_id, field_name="model_id")


@dataclass(frozen=True)
class DesiredState:
    """Target control posture requested by higher-level callers."""

    mode: DesiredControlMode = DesiredControlMode.STOPPED
    target_model_id: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate desired-state invariants without implying runtime behavior."""

        if self.mode is DesiredControlMode.RUNNING and self.target_model_id is None:
            raise ControlStateError(
                "desired.target_model_id is required when desired.mode is RUNNING"
            )

        if self.target_model_id is not None:
            _require_model_id(self.target_model_id, field_name="target_model_id")

        if self.mode is DesiredControlMode.STOPPED and self.target_model_id is not None:
            raise ControlStateError(
                "desired.target_model_id must be omitted when desired.mode is STOPPED"
            )


@dataclass(frozen=True)
class ObservedRuntimeState:
    """Observed local runtime posture without implying control behavior."""

    phase: RuntimePhase = RuntimePhase.UNKNOWN
    active_model_id: Optional[str] = None
    detail: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate observed runtime-state shape as raw observation data."""

        if self.active_model_id is not None:
            _require_model_id(self.active_model_id, field_name="active_model_id")

        if self.phase in (RuntimePhase.STOPPED, RuntimePhase.UNKNOWN) and self.active_model_id is not None:
            raise ControlStateError(
                "observed.active_model_id must be omitted when observed.phase is STOPPED or UNKNOWN"
            )


@dataclass(frozen=True)
class ControlState:
    """Single canonical ownership point for controller-visible state."""

    desired: DesiredState = field(default_factory=DesiredState)
    observed: ObservedRuntimeState = field(default_factory=ObservedRuntimeState)
    active_model: Optional[ActiveModelIdentity] = None
    health: HealthSummary = field(default_factory=HealthSummary)
    registry: ModelRegistryState = field(default_factory=ModelRegistryState)
    config: ControlConfig = field(default_factory=ControlConfig)

    def __post_init__(self) -> None:
        """Validate canonical relationships across controller-visible state."""

        if self.active_model is not None and self.observed.phase in (
            RuntimePhase.STOPPED,
            RuntimePhase.UNKNOWN,
        ):
            raise ControlStateError(
                "active_model must be omitted when observed.phase is STOPPED or UNKNOWN"
            )

        if self.observed.phase is RuntimePhase.RUNNING:
            if self.active_model is None:
                raise ControlStateError(
                    "active_model is required when observed.phase is RUNNING"
                )
            if self.observed.active_model_id is None:
                raise ControlStateError(
                    "observed.active_model_id is required when observed.phase is RUNNING"
                )
            if self.active_model.model_id != self.observed.active_model_id:
                raise ControlStateError(
                    "active_model.model_id must match observed.active_model_id when observed.phase is RUNNING"
                )

        if (
            self.desired.mode is DesiredControlMode.RUNNING
            and self.active_model is not None
            and self.observed.phase is RuntimePhase.RUNNING
            and self.desired.target_model_id != self.active_model.model_id
        ):
            raise ControlStateError(
                "desired.target_model_id must match active_model.model_id when observed.phase is RUNNING"
            )


def _require_model_id(value: str, field_name: str) -> None:
    """Validate a model identifier used by control-state contracts."""

    if not value.strip():
        raise ControlStateError(f"{field_name} must be a non-empty string")
