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

    @classmethod
    def stopped(cls) -> "DesiredState":
        """Construct the inert desired-state posture."""

        return cls(mode=DesiredControlMode.STOPPED)

    @classmethod
    def running(cls, model_id: str) -> "DesiredState":
        """Construct a running desired-state posture for a model."""

        return cls(mode=DesiredControlMode.RUNNING, target_model_id=model_id)

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

    @classmethod
    def unknown(cls, detail: Optional[str] = None) -> "ObservedRuntimeState":
        """Construct an unknown observed runtime posture."""

        return cls(phase=RuntimePhase.UNKNOWN, detail=detail)

    @classmethod
    def stopped(cls, detail: Optional[str] = None) -> "ObservedRuntimeState":
        """Construct a stopped observed runtime posture."""

        return cls(phase=RuntimePhase.STOPPED, detail=detail)

    @classmethod
    def starting(
        cls, model_id: Optional[str] = None, detail: Optional[str] = None
    ) -> "ObservedRuntimeState":
        """Construct a transitional starting runtime posture."""

        return cls(
            phase=RuntimePhase.STARTING,
            active_model_id=model_id,
            detail=detail,
        )

    @classmethod
    def running(cls, model_id: str, detail: Optional[str] = None) -> "ObservedRuntimeState":
        """Construct a running observed runtime posture."""

        return cls(
            phase=RuntimePhase.RUNNING,
            active_model_id=model_id,
            detail=detail,
        )

    @classmethod
    def stopping(
        cls, model_id: Optional[str] = None, detail: Optional[str] = None
    ) -> "ObservedRuntimeState":
        """Construct a transitional stopping runtime posture."""

        return cls(
            phase=RuntimePhase.STOPPING,
            active_model_id=model_id,
            detail=detail,
        )

    @property
    def is_transitioning(self) -> bool:
        """Return whether the observed runtime is in a transition phase."""

        return self.phase in (RuntimePhase.STARTING, RuntimePhase.STOPPING)

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

    @classmethod
    def stopped(
        cls,
        *,
        health: Optional[HealthSummary] = None,
        registry: Optional[ModelRegistryState] = None,
        config: Optional[ControlConfig] = None,
    ) -> "ControlState":
        """Construct an inert canonical stopped control state."""

        return cls(
            desired=DesiredState.stopped(),
            observed=ObservedRuntimeState.stopped(),
            health=health or HealthSummary(),
            registry=registry or ModelRegistryState(),
            config=config or ControlConfig(),
        )

    @classmethod
    def running(
        cls,
        model_id: str,
        *,
        display_name: Optional[str] = None,
        revision: Optional[str] = None,
        health: Optional[HealthSummary] = None,
        registry: Optional[ModelRegistryState] = None,
        config: Optional[ControlConfig] = None,
        detail: Optional[str] = None,
    ) -> "ControlState":
        """Construct a steady-state running control snapshot."""

        active_model = ActiveModelIdentity(
            model_id=model_id,
            display_name=display_name,
            revision=revision,
        )
        return cls(
            desired=DesiredState.running(model_id),
            observed=ObservedRuntimeState.running(model_id=model_id, detail=detail),
            active_model=active_model,
            health=health or HealthSummary(),
            registry=registry or ModelRegistryState(),
            config=config or ControlConfig(),
        )

    @property
    def is_running(self) -> bool:
        """Return whether the canonical state is in steady running posture."""

        return self.observed.phase is RuntimePhase.RUNNING

    @property
    def is_transitioning(self) -> bool:
        """Return whether the observed runtime is in a transition phase."""

        return self.observed.is_transitioning

    @property
    def has_active_model(self) -> bool:
        """Return whether a canonical active model identity is present."""

        return self.active_model is not None

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
